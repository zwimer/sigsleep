import argparse
import signal
import time
import sys
import os

from ._version import __version__


def _handler(total: float, start: int, *_) -> None:
    """
    Bind total and start to make into a signal handler that prints elapsed time
    """
    remain: int = round(total - (time.time_ns() - start) / 1e9)
    t: str = str(int(total) if int(total) == total else total)
    print(f"sleep: about {remain} seconds(s) left out of the original {t}")


def sigsleep(seconds: float, sig: signal.Signals) -> int:
    """
    Sleep, print elapsed time on intercepting signal
    :return Exit code
    """
    start: int = time.time_ns()
    signal.signal(sig, lambda *_: _handler(seconds, start))
    try:
        time.sleep(seconds)
    except KeyboardInterrupt:
        return 130
    return 0


def cli() -> None:
    """
    CLI for sigsleep
    Default signal is SIGINFO if it exists, else SIGUSR1
    """
    base: str = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(prog=base)
    parser.add_argument("--version", action="version", version=f"{base} {__version__}")
    parser.add_argument("seconds", type=float, help="The number of seconds to sleep")
    to_signal = lambda d: signal.Signals(int(d))
    to_signal.__name__ = "signal"  # Cleaner output
    parser.add_argument(
        "--signal",
        type=to_signal,
        help="The signal to intercept",
        default=signal.SIGINFO if hasattr(signal, "SIGINFO") else signal.SIGUSR1,
    )
    ns = parser.parse_args(sys.argv[1:])
    sys.exit(sigsleep(ns.seconds, ns.signal))


if __name__ == "__main__":
    cli()
