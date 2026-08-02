"""The graded rows of the interval table: presence, fitted over what nothing saw.

A `Stop` and the next submit in that session bound a span the store says nothing
about. Claude had finished; the human came back at the end of it; in between the
store is silent. That silence is the largest single block of time in the data —
128 hours of it across the store against 15 hours of Claude-active time — so how
it is counted decides most of the answer.

Nothing observes it, so nothing here claims to. Each gap becomes one
`human_present` row whose `confidence` is a fitted probability rather than a
verdict: the store's other rows carry 1.0 because an event proves them, and
these carry whatever the model gives them ([Measurement
Prototype](/docs/measurement-prototype.md), assumption 8). Gaps tile the session
against the turns — a turn runs submit to `Stop`, a gap runs `Stop` to the next
submit — so the two never overlap.

The model is a two-component mixture over log gap length: a working mode, where
the human read the reply and typed the next prompt, and an away mode, where they
came back later. Fitted on the store's own gaps, the working mode sits at
73 seconds with 98.3 % of the gaps and the away mode at 5.8 hours with the rest,
and presence falls below even odds at about 2.2 hours.

**The two components share one variance, and that constraint is the point.**
Let them vary freely and the likelihood is better — the fit puts a narrow
component on the bulk of the gaps and a broad one across everything else — but
then the shortest gaps in the store belong to the *broad* component, so a
two-second gap reads as absence. A presence probability that is not monotone in
gap length is not a presence probability. Tying the variance makes the posterior
a logistic function of log duration: the crossover and its sharpness are both
fitted, which is what replaces the hand-picked threshold the doc set out to
avoid.

Fitting is expectation-maximization, written here rather than imported. It is
about thirty lines for one dimension and two components, against a
scientific-stack dependency this repo — a linting playbook consumer repos
install — should not carry for it. EM finds a local optimum, so every fit runs
from several deterministic starts and keeps the best-scoring one that converged.
That matters here rather than in theory: on the store's own gaps only the widest
start escapes the valley where both means collapse onto the overall mean and the
posterior goes flat, and the starts that fall into it never settle at all.

What the fit cannot do is decline. Two modes are what it looks for, so two modes
are what it finds, in a window whose gaps were all worked straight through as
readily as in one holding a night's sleep. `MixtureFit.summary` exists for that:
a working mode of a minute against an away mode of hours is a model worth
believing, and two modes a minute apart is the same window told twice.
"""

import math
import statistics
from collections.abc import Sequence
from dataclasses import dataclass

import pandas as pd

from dev_playbook.measure.intervals import INTERRUPTED, STOP, SUBMIT, interval_frame

HUMAN_PRESENT = "human_present"

GAP_COLUMNS = ("start", "end", "session_id", "seconds")

GAP_DTYPES = {
    "start": "datetime64[us, UTC]",
    "end": "datetime64[us, UTC]",
    "seconds": "float64",
}

# Four free parameters are fitted, so a handful of gaps would fit noise and
# report it as a model. Any real window clears this by two orders of magnitude.
MINIMUM_GAPS = 10

# EM has converged when no parameter moves more than this in a step. The
# iteration cap is generous against the store's own fit, which lands in under a
# hundred steps from the start that works; a start still moving at the cap is in
# the flat valley between two collapsed means, and is discarded.
TOLERANCE = 1e-10
MAX_ITERATIONS = 500


class PresenceError(Exception):
    """Gaps this module will not fit a presence model to.

    Raised rather than defaulted, because every alternative is a number that
    looks like a measurement: a mixture fitted to nine gaps, or a posterior so
    flat that every gap in the window carries the same confidence, would both
    flow into the interval table indistinguishable from a good fit.
    """


@dataclass(frozen=True)
class Component:
    """One mode of the fitted mixture: its share of the gaps, and where it sits."""

    weight: float
    mean: float

    @property
    def median_seconds(self) -> float:
        """The gap length at the middle of this mode.

        The mean is in log seconds, where the fit happens; this is that mean
        back in seconds, which for a lognormal is the median rather than the
        mean gap length.
        """
        return math.exp(self.mean)


@dataclass(frozen=True)
class MixtureFit:
    """The fitted presence model, kept whole so a run can print it.

    The parameters travel with the numbers they produced. A confidence of 0.31
    on a two-hour gap is only meaningful beside the model that assigned it, and
    a model that lives inside the function that fitted it cannot be argued with.

    `sd` is the standard deviation both components share, in log seconds.
    """

    present: Component
    absent: Component
    sd: float
    gaps: int
    iterations: int
    log_likelihood: float

    def presence(self, seconds: float) -> float:
        """The probability the human was at the machine through a gap this long.

        Strictly decreasing in `seconds` — the shared variance is what
        guarantees that — so it reads as the graded threshold it is.
        """
        length = math.log(seconds)
        return _sigmoid(
            _log_weighted_density(length, self.present, self.sd)
            - _log_weighted_density(length, self.absent, self.sd)
        )

    @property
    def crossover_seconds(self) -> float:
        """The gap length where presence falls to even odds.

        The soft threshold the fit found, reported because it is the one number
        a reader will want to argue with. It is not a cutoff: the shared
        variance sets how quickly the probability falls through it. The heavier
        the working mode, the further out it sits — a prior that says most gaps
        are worked through takes a long silence to overturn.
        """
        odds = math.log(self.present.weight / self.absent.weight)
        midpoint = (self.present.mean + self.absent.mean) / 2
        separation = self.absent.mean - self.present.mean
        return math.exp(midpoint + self.sd**2 * odds / separation)

    def summary(self) -> str:
        """The fitted model as text, for the run that used it to print."""
        return "\n".join(
            (
                f"presence mixture over {self.gaps} gaps "
                f"({self.iterations} EM steps, "
                f"log-likelihood {self.log_likelihood:.2f})",
                f"  working mode: {self.present.weight:.1%} of gaps, median "
                f"{human_seconds(self.present.median_seconds)}",
                f"  away mode:    {self.absent.weight:.1%} of gaps, median "
                f"{human_seconds(self.absent.median_seconds)}",
                f"  shared log-sd {self.sd:.3f}; presence reaches even odds at "
                f"{human_seconds(self.crossover_seconds)}",
            )
        )


@dataclass(frozen=True)
class Presence:
    """The graded interval rows, and the model that graded them."""

    frame: pd.DataFrame
    fit: MixtureFit


def stop_gaps(events: pd.DataFrame) -> pd.DataFrame:
    """Every span from a `Stop` to the next submit in the same session.

    Columns are `start`, `end`, `session_id` and `seconds`. Rows are walked in
    `id` order — the store's only total order — and a gap is only emitted for a
    `Stop` that is *immediately* followed by a submit among that session's stops
    and submits. A `Stop` with another `Stop` before the next submit ran a turn
    inside the wider span, which is therefore not one idle stretch; counting
    both would count the inner one twice.

    A gap of zero or less means the two hooks arrived out of order against the
    ids they were given. That inversion is raised rather than clamped: it is
    evidence about the capture path, and a duration of zero has no logarithm to
    fit.
    """
    marks = events[events["event"].isin((STOP, SUBMIT))].sort_values("id")
    rows = []
    for session, group in marks.groupby("session_id"):
        ordered = list(group.itertuples())
        for stop, submit in zip(ordered, ordered[1:], strict=False):
            if stop.event != STOP or submit.event != SUBMIT:
                continue
            seconds = (submit.received_at - stop.received_at).total_seconds()
            if seconds <= 0:
                raise PresenceError(
                    f"session {session}: rows {stop.id} and {submit.id} are "
                    f"{seconds} s apart, so the submit precedes the Stop it follows"
                )
            rows.append(
                {
                    "start": stop.received_at,
                    "end": submit.received_at,
                    "session_id": session,
                    "seconds": seconds,
                }
            )
    return pd.DataFrame(rows, columns=list(GAP_COLUMNS)).astype(GAP_DTYPES)


def fit_presence(seconds: Sequence[float]) -> MixtureFit:
    """The two-component presence mixture fitted to observed gap lengths.

    Fitted in log seconds from several deterministic starts, keeping the
    converged fit with the highest log-likelihood. Deterministic throughout:
    the same gaps give the same model, so a confidence in the interval table
    can be reproduced from the store rather than only from a run.
    """
    if len(seconds) < MINIMUM_GAPS:
        raise PresenceError(
            f"{len(seconds)} gaps is too few to fit a two-component mixture "
            f"(needs {MINIMUM_GAPS})"
        )
    negative = [value for value in seconds if value <= 0]
    if negative:
        raise PresenceError(f"gap lengths must be positive, got {negative[0]}")

    lengths = sorted(math.log(value) for value in seconds)
    spread = statistics.pstdev(lengths)
    if spread == 0:
        raise PresenceError(f"every one of the {len(seconds)} gaps is the same length")

    half = len(lengths) // 2
    starts = (
        # Widest first: on the store's own gaps it is the only one of these that
        # escapes the valley where both means converge on the overall mean.
        (lengths[0], lengths[-1]),
        (lengths[len(lengths) // 10], lengths[-1 - len(lengths) // 10]),
        (statistics.fmean(lengths[:half]), statistics.fmean(lengths[half:])),
    )
    fits = [
        fit
        for fit in (_maximize(lengths, low, high, spread) for low, high in starts)
        if fit is not None
    ]
    if not fits:
        raise PresenceError(
            f"no start converged within {MAX_ITERATIONS} EM steps over "
            f"{len(seconds)} gaps"
        )
    return max(fits, key=lambda fit: fit.log_likelihood)


def presence_intervals(events: pd.DataFrame) -> Presence:
    """One graded `human_present` row per gap, oldest first, and the fit behind them.

    Feed it cleaned events, as with the definitive rows: a task-notification
    pseudo-prompt left in ends a gap the human never came back from, which both
    shortens the gap and feeds the fit a length nobody waited.
    """
    gaps = stop_gaps(events)
    fit = fit_presence(list(gaps["seconds"]))
    frame = interval_frame(
        {
            "start": gap.start,
            "end": gap.end,
            "state": HUMAN_PRESENT,
            "session_id": gap.session_id,
            "confidence": fit.presence(gap.seconds),
        }
        for gap in gaps.itertuples()
    )
    return Presence(
        frame.sort_values(["start", "session_id"], kind="stable").reset_index(
            drop=True
        ),
        fit,
    )


def grade_interrupts(frame: pd.DataFrame, fit: MixtureFit) -> pd.DataFrame:
    """`frame` with each `interrupted` row's confidence refitted to its own length.

    An interrupted turn is closed at the next submit, which is the interrupt
    instant only if the human resubmitted straight away. Everything after the
    interrupt is the same unobserved thing a `Stop`-to-submit gap is, so it takes
    the same fitted probability: an interrupt the human returned from in thirty
    seconds stays all but certain, and one that swallowed a night falls to near
    zero along with the claim that Claude was working through it.

    Left at 1.0 these rows are the loudest thing in the picture — over the whole
    store one 15.7-hour row carries 83 % of all interrupted time, drawn as solid
    as a measured turn. Grading is what stops the longest and least trustworthy
    span from also being the most visible.

    Every other state is returned untouched, so this composes onto a table that
    already holds definitive and graded rows alike.
    """
    if frame.empty:
        return frame
    lengths = (frame["end"] - frame["start"]).dt.total_seconds()
    if (lengths[frame["state"] == INTERRUPTED] <= 0).any():
        raise PresenceError("an interrupted row spans zero seconds, which has no fit")
    graded = [
        fit.presence(length) if state == INTERRUPTED else confidence
        for state, length, confidence in zip(
            frame["state"], lengths, frame["confidence"], strict=True
        )
    ]
    return frame.assign(
        confidence=pd.Series(graded, index=frame.index, dtype="float64")
    )


def human_seconds(seconds: float) -> str:
    """A duration as the coarsest two units that describe it, for reading.

    The quantities here span seconds to hours in the same report, and a summary
    line that prints 20729 s beside 73 s makes the reader do the conversion the
    model exists to explain. Public because the timeline's hover labels face the
    same spread and must read the same way.
    """
    if seconds < 60:
        return f"{seconds:.0f}s"
    if seconds < 3600:
        return f"{seconds // 60:.0f}m {seconds % 60:.0f}s"
    return f"{seconds // 3600:.0f}h {seconds % 3600 // 60:.0f}m"


# --- the mixture's arithmetic -------------------------------------------------


def _sigmoid(z: float) -> float:
    """The logistic function, evaluated so neither tail overflows."""
    if z >= 0:
        return 1 / (1 + math.exp(-z))
    weight = math.exp(z)
    return weight / (1 + weight)


def _log_weighted_density(length: float, component: Component, sd: float) -> float:
    """One component's weighted log density at `length`, less the shared constant.

    The `1 / (sd * sqrt(2 pi))` both components share is dropped: every use
    either divides two of these by each other or adds the constant back once,
    and leaving it out keeps all of them in the log domain.
    """
    return math.log(component.weight) - (length - component.mean) ** 2 / (2 * sd**2)


def _log_sum_exp(left: float, right: float) -> float:
    """`log(exp(left) + exp(right))`, evaluated without leaving the log domain."""
    larger = max(left, right)
    return larger + math.log(math.exp(left - larger) + math.exp(right - larger))


# --- expectation-maximization -------------------------------------------------


def _maximize(
    lengths: list[float], low: float, high: float, sd: float
) -> MixtureFit | None:
    """EM from one start, or None if it collapsed or was still moving at the cap.

    A start that drives either component's weight to nothing, or that has not
    settled within `MAX_ITERATIONS`, is a start that found nothing — the caller
    has others, and reporting the state it stopped in would report a model that
    was still moving.
    """
    total = len(lengths)
    weight = 0.5
    for step in range(1, MAX_ITERATIONS + 1):
        first, second = Component(weight, low), Component(1 - weight, high)
        shares = [
            _sigmoid(
                _log_weighted_density(length, first, sd)
                - _log_weighted_density(length, second, sd)
            )
            for length in lengths
        ]
        claimed = math.fsum(shares)
        if claimed == 0 or claimed == total:
            return None
        moved_low = (
            math.fsum(
                share * length for share, length in zip(shares, lengths, strict=True)
            )
            / claimed
        )
        moved_high = math.fsum(
            (1 - share) * length for share, length in zip(shares, lengths, strict=True)
        ) / (total - claimed)
        moved_sd = math.sqrt(
            math.fsum(
                share * (length - moved_low) ** 2
                + (1 - share) * (length - moved_high) ** 2
                for share, length in zip(shares, lengths, strict=True)
            )
            / total
        )
        moved_weight = claimed / total
        settled = (
            max(
                abs(moved_low - low),
                abs(moved_high - high),
                abs(moved_sd - sd),
                abs(moved_weight - weight),
            )
            < TOLERANCE
        )
        low, high, sd, weight = moved_low, moved_high, moved_sd, moved_weight
        if settled:
            return _fitted(lengths, low, high, sd, weight, step)
    return None


def _fitted(
    lengths: list[float],
    low: float,
    high: float,
    sd: float,
    weight: float,
    steps: int,
) -> MixtureFit:
    """The converged parameters as a `MixtureFit`, scored on the gaps that made it.

    The lower mean is the working mode and so the present one: a human who is
    there comes back sooner than one who is not.
    """
    first, second = Component(weight, low), Component(1 - weight, high)
    present, absent = (first, second) if low <= high else (second, first)
    constant = math.log(sd * math.sqrt(2 * math.pi))
    log_likelihood = math.fsum(
        _log_sum_exp(
            _log_weighted_density(length, present, sd),
            _log_weighted_density(length, absent, sd),
        )
        - constant
        for length in lengths
    )
    return MixtureFit(present, absent, sd, len(lengths), steps, log_likelihood)
