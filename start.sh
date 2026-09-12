#!/usr/bin/env bash
set -e

# Catchaj — Job Application Engine Quick Action Script
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

PYTHON="$PROJECT_DIR/.venv/bin/python"
if [ ! -f "$PYTHON" ]; then
    PYTHON="python3"
fi

PID_DIR="$PROJECT_DIR/.pids"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$PID_DIR" "$LOG_DIR"

APP_PID_FILE="$PID_DIR/app.pid"
DAEMON_PID_FILE="$PID_DIR/daemon.pid"

check_running() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        local pid
        pid=$(cat "$pid_file" 2>/dev/null || echo "")
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

start_app() {
    local existing_pid
    existing_pid=$(lsof -ti:5001 2>/dev/null || true)
    if [ -n "$existing_pid" ]; then
        echo "$existing_pid" > "$APP_PID_FILE"
        echo "[✓] Dashboard is already running (PID $existing_pid) at http://127.0.0.1:5001"
        return
    fi
    echo "[*] Starting Dashboard (app.py)..."
    nohup "$PYTHON" app.py > "$LOG_DIR/app.log" 2>&1 &
    echo $! > "$APP_PID_FILE"
    sleep 1
    echo "[✓] Dashboard started at http://127.0.0.1:5001 (PID $(cat "$APP_PID_FILE"))"
}

start_daemon() {
    if check_running "$DAEMON_PID_FILE"; then
        echo "[✓] Scraper daemon is already running (PID $(cat "$DAEMON_PID_FILE"))"
    else
        echo "[*] Starting Scraper Daemon (daemon.py - hourly 24h market scans)..."
        nohup "$PYTHON" daemon.py > "$LOG_DIR/daemon.log" 2>&1 &
        echo $! > "$DAEMON_PID_FILE"
        sleep 1
        echo "[✓] Scraper daemon started (PID $(cat "$DAEMON_PID_FILE"))"
    fi
}

stop_all() {
    echo "[*] Stopping services..."
    local port_pid
    port_pid=$(lsof -ti:5001 2>/dev/null || true)
    if [ -n "$port_pid" ]; then
        echo "[-] Stopping Dashboard on port 5001 (PID $port_pid)..."
        kill -9 $port_pid 2>/dev/null || true
    fi
    if check_running "$APP_PID_FILE"; then
        local pid
        pid=$(cat "$APP_PID_FILE" 2>/dev/null || echo "")
        [ -n "$pid" ] && kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$APP_PID_FILE"

    if check_running "$DAEMON_PID_FILE"; then
        local pid
        pid=$(cat "$DAEMON_PID_FILE" 2>/dev/null || echo "")
        if [ -n "$pid" ]; then
            echo "[-] Stopping Daemon (PID $pid)..."
            kill -9 "$pid" 2>/dev/null || true
        fi
    fi
    rm -f "$DAEMON_PID_FILE"

    pkill -f "python.*app\.py" 2>/dev/null || true
    pkill -f "python.*daemon\.py" 2>/dev/null || true
    echo "[✓] All services stopped."
}

show_status() {
    echo "=========================================================="
    echo "            CATCHAJ SERVICE STATUS"
    echo "=========================================================="
    if check_running "$APP_PID_FILE"; then
        echo "Dashboard: RUNNING (PID $(cat "$APP_PID_FILE")) -> http://127.0.0.1:5001"
    else
        echo "Dashboard: STOPPED"
    fi

    if check_running "$DAEMON_PID_FILE"; then
        echo "Daemon:    RUNNING (PID $(cat "$DAEMON_PID_FILE")) -> Scanning hourly (past 24h)"
    else
        echo "Daemon:    STOPPED"
    fi
    echo "----------------------------------------------------------"
    "$PYTHON" orchestrator.py status
    echo "=========================================================="
}

run_scan_now() {
    echo "[*] Running immediate 24-hour market scan (HiringCafe + JobSpy)..."
    "$PYTHON" orchestrator.py scan --hours 24 --count 8
    echo "[*] Processing automatic tailoring for qualified roles..."
    "$PYTHON" orchestrator.py tailor
    echo "[✓] Scan & tailoring complete. Run './start.sh status' or open http://127.0.0.1:5001 to view."
}

ACTION="${1:-start}"

case "$ACTION" in
    start)
        start_app
        start_daemon
        echo ""
        echo "=========================================================="
        echo "🚀 Engine is LIVE!"
        echo "   • Dashboard: http://127.0.0.1:5001"
        echo "   • Logs:      tail -f logs/app.log logs/daemon.log"
        echo "   • Stop:      ./start.sh stop"
        echo "   • Status:    ./start.sh status"
        echo "   • Fast Scan: ./start.sh scan"
        echo "=========================================================="
        ;;
    stop)
        stop_all
        ;;
    restart)
        stop_all
        sleep 1
        start_app
        start_daemon
        ;;
    status)
        show_status
        ;;
    scan)
        run_scan_now
        ;;
    *)
        echo "Usage: ./start.sh [start|stop|restart|status|scan]"
        exit 1
        ;;
esac
