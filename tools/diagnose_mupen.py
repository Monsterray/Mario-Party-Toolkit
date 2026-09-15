#!/usr/bin/env python3
"""Run ROMs sequentially, saving logs and macOS screenshots without claiming boot success."""
import argparse
import hashlib
import json
import signal
import subprocess
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mupen', required=True, type=Path)
    parser.add_argument('--cwd', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--case', action='append', required=True, help='NAME=/absolute/ROM.z64')
    parser.add_argument('--seconds', type=float, default=45)
    parser.add_argument('--gfx', default='mupen64plus-video-glide64mk2')
    parser.add_argument('--set', dest='settings', action='append', default=[])
    args = parser.parse_args()
    if args.seconds <= 0:
        parser.error('--seconds must be positive')
    cases = []
    for case in args.case:
        name, sep, rom = case.partition('=')
        if not sep or not name or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in name):
            parser.error('Use a unique lowercase name containing only letters, digits, - or _')
        path = Path(rom).expanduser().resolve(strict=True)
        if name in [n for n, _ in cases]:
            parser.error('Case names must be unique')
        cases.append((name, path))
    executable = str(args.mupen.expanduser().resolve(strict=True))
    cwd = args.cwd.expanduser().resolve(strict=True)
    args.output = args.output.expanduser().resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    reports = []
    for name, rom in cases:
        command = [executable, '--gfx', args.gfx, '--windowed', '--resolution', '640x480', '--nosaveoptions']
        for setting in args.settings:
            command += ['--set', setting]
        command.append(str(rom))
        report = dict(name=name, rom=str(rom), sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),
                      command=command, cwd=str(cwd), screenshots=[], visual_result='unreviewed')
        log = args.output / (name + '.log')
        report['log'] = str(log)
        print('Starting ' + name, flush=True)
        started = time.monotonic()
        with log.open('x') as stream:
            proc = subprocess.Popen(command, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT)
            try:
                for seconds in (min(10, args.seconds / 2), args.seconds):
                    while proc.poll() is None and time.monotonic() - started < seconds:
                        time.sleep(0.2)
                    if proc.poll() is not None:
                        break
                    screenshot = args.output / f'{name}-{seconds:g}s.png'
                    capture = subprocess.run(['/usr/sbin/screencapture', '-x', str(screenshot)],
                                             capture_output=True, text=True, timeout=10)
                    report['screenshots'].append(dict(path=str(screenshot),
                        elapsed=round(time.monotonic() - started, 2),
                        returncode=capture.returncode, error=capture.stderr))
            finally:
                report['running_at_end'] = proc.poll() is None
                if proc.poll() is None:
                    proc.send_signal(signal.SIGINT)
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()
                report['returncode'] = proc.returncode
                report['elapsed'] = round(time.monotonic() - started, 2)
                reports.append(report)
                (args.output / 'report.json').write_text(json.dumps(reports, indent=2) + '\n')
        print(json.dumps({k: report[k] for k in ('name', 'running_at_end', 'returncode', 'elapsed')}), flush=True)


if __name__ == '__main__':
    main()
