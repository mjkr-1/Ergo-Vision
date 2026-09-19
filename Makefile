.PHONY: setup run doctor test build check demo

setup:
	bash scripts/setup_mac.sh

run:
	bash scripts/run_mac.sh

doctor:
	bash scripts/doctor_mac.sh

test:
	. .venv/bin/activate && cd backend && python -m pytest tests/ -v

build:
	cd frontend && npm run build

check:
	bash scripts/check.sh

demo:
	. .venv/bin/activate && cd backend && DEMO_MODE=1 python -m uvicorn app.main:app --reload --port 8000

mac-app:
	bash scripts/install_mac_app.sh

stop:
	bash scripts/stop_mac.sh
