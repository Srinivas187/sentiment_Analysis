"""
Automated runner for the project (development mode)

Usage:
  python run_all.py            # initialize DB, create dummy model if missing, start backend & frontend
  python run_all.py --noinstall # skip installing requirements

This script is intended for local development only (not production).
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_PY = sys.executable
FRONTEND_PORT = int(os.getenv('FRONTEND_PORT', 8000))


def install_requirements():
    print('==> Installing Python dependencies (this may take a while)...')
    cmd = [VENV_PY, '-m', 'pip', 'install', '-r', str(ROOT / 'requirements.txt')]
    proc = subprocess.Popen(cmd)
    proc.wait()
    if proc.returncode != 0:
        print('[!] pip install failed. Please run manually:')
        print('    ' + ' '.join(cmd))
        return False
    return True


def init_database():
    print('==> Initializing database...')
    try:
        from database.init_db import create_database_and_tables
        ok = create_database_and_tables()
        if ok:
            print('[OK] Database initialized')
            return True
        else:
            print('[!] Database initialization returned False')
            return False
    except Exception as e:
        print(f'[!] Database initialization failed: {e}')
        return False


def ensure_dummy_model():
    from backend.config import MODEL_DIR
    model_path = MODEL_DIR / 'best_model.h5'
    vocab = MODEL_DIR / 'vocab.pkl'
    meta = MODEL_DIR / 'model_metadata.pkl'

    if model_path.exists() and vocab.exists() and meta.exists():
        print('[OK] Model artifacts present')
        return True

    print('==> Creating dummy model artifacts (for local dev) ...')
    cmd = [VENV_PY, str(ROOT / 'ml' / 'create_dummy_model_files.py')]
    proc = subprocess.Popen(cmd)
    proc.wait()
    return proc.returncode == 0


def stream_process(proc, name):
    def _reader(pipe, prefix):
        for line in iter(pipe.readline, b''):
            try:
                print(f'[{prefix}] ' + line.decode('utf-8', errors='replace').rstrip())
            except Exception:
                pass

    threading.Thread(target=_reader, args=(proc.stdout, name), daemon=True).start()
    threading.Thread(target=_reader, args=(proc.stderr, name + '-ERR'), daemon=True).start()


def start_backend():
    print('==> Starting backend (Flask) ...')
    cmd = [VENV_PY, str(ROOT / 'backend' / 'app.py')]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stream_process(proc, 'BACKEND')
    return proc


def start_frontend():
    print(f'==> Serving frontend at http://localhost:{FRONTEND_PORT} ...')
    # run in frontend folder: python -m http.server 8000
    cmd = [VENV_PY, '-m', 'http.server', str(FRONTEND_PORT)]
    proc = subprocess.Popen(cmd, cwd=str(ROOT / 'frontend'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stream_process(proc, 'FRONTEND')
    return proc


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--noinstall', action='store_true', help='Do not run pip install')
    args = parser.parse_args()

    if not args.noinstall:
        ok = install_requirements()
        if not ok:
            print('[!] Aborting due to pip install failure')
            sys.exit(1)

    ok = init_database()
    if not ok:
        print('[!] Aborting due to DB initialization failure')
        sys.exit(1)

    ok = ensure_dummy_model()
    if not ok:
        print('[!] Failed to ensure dummy model artifacts')
        sys.exit(1)

    backend_proc = start_backend()
    frontend_proc = start_frontend()

    print('\n==> All services started. Press Ctrl+C to stop.')

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print('[!] Backend process exited')
                break
            if frontend_proc.poll() is not None:
                print('[!] Frontend process exited')
                break
    except KeyboardInterrupt:
        print('\nStopping services...')
    finally:
        for p in (backend_proc, frontend_proc):
            try:
                p.terminate()
            except Exception:
                pass
        print('Done')


if __name__ == '__main__':
    main()
