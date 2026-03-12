#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-incremental}"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

case "$MODE" in
	full)
		echo "[$TS] Running full sync"
		trisort sync full
		;;
	incremental)
		echo "[$TS] Running incremental sync"
		trisort sync incremental
		;;
	dry-run)
		echo "[$TS] Running dry-run sync"
		trisort sync dry-run
		;;
	*)
		echo "Unsupported mode: $MODE" >&2
		exit 2
		;;
esac
