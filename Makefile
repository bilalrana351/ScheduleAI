# Define shell
SHELL := /bin/bash

# Colors for terminal output
BLUE := \033[34m
GREEN := \033[32m
RESET := \033[0m

# Default target
.PHONY: all
all: run-all

# Run both servers
.PHONY: run-all
run-all:
	@echo -e "$(GREEN)Starting both servers...$(RESET)"
	@make -j2 run-backend run-frontend

# Run backend server
.PHONY: run-backend
run-backend:
	@echo -e "$(BLUE)Starting Backend Server...$(RESET)"
	cd backend && source .venv/bin/activate && python src/server.py

# Run frontend server
.PHONY: run-frontend
run-frontend:
	@echo -e "$(BLUE)Starting Frontend Server...$(RESET)"
	cd frontend && npm run dev

# Stop all servers
.PHONY: stop
stop:
	@echo -e "$(GREEN)Stopping all servers...$(RESET)"
	@pgrep -f "python3 server.py" | xargs kill -9 2>/dev/null || echo "Backend server not running"
	@pgrep -f "npm run dev" | xargs kill -9 2>/dev/null || echo "Frontend server not running"

# Install dependencies
.PHONY: install
install:
	@echo -e "$(GREEN)Installing backend dependencies...$(RESET)"
	cd backend && pip3 install -r requirements.txt
	@echo -e "$(GREEN)Installing frontend dependencies...$(RESET)"
	cd frontend && npm install

# Clean
.PHONY: clean
clean:
	@echo -e "$(GREEN)Cleaning up...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -r {} + 2>/dev/null || true