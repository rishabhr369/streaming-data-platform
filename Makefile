.PHONY: setup up down logs ps clean reset config init-volumes clean-data clean-datalake clean-checkpoints clean-all data-stats help

# Setup configuration and dependencies
setup:
	@echo "Setting up Mini Cluster from config.yml..."
	@./scripts/setup.sh

# Generate .env from config.yml (without interactive setup)
config:
	@echo "Generating .env from config.yml..."
	@python3 config_loader.py generate-env
	@echo "✅ Configuration updated!"

up:
	@if [ ! -f .env ]; then echo "⚠️  .env file not found. Run 'make setup' or 'make config' first."; exit 1; fi
	@echo "🚀 Starting Mini Cluster..."
	@$(MAKE) init-volumes
	docker compose up -d --build

logs:
	docker compose logs -f --tail=200

ps:
	docker compose ps

down:
	docker compose down

clean:
	docker compose down -v

reset: clean up

# Initialize data volumes with proper permissions (automatically called by 'up')
init-volumes:
	@echo "🔧 Initializing data volumes with proper permissions..."
	@./scripts/init-volumes.sh

# Show current configuration
show-config:
	@echo "Current configuration from config.yml:"
	@echo "====================================="
	@python3 config_loader.py export-shell

# === DATA CLEANUP TARGETS ===

# Clean all locally persisted data (datalake + checkpoints)
clean-data:
	@echo "🧹 CLEANING ALL LOCAL DATA"
	@echo "⚠️  This will permanently delete:"
	@echo "   • All datalake data (parquet files)"
	@echo "   • All checkpoint data (streaming state)"
	@if [ -d "./data" ]; then \
		echo "📊 Current data volume:"; \
		du -sh ./data/datalake ./data/checkpoints 2>/dev/null || echo "   No data directories found"; \
	fi
	@echo ""
	@read -p "Are you sure you want to delete ALL local data? [y/N]: " confirm && [ "$$confirm" = "y" ]
	@echo "🗑️  Removing datalake and checkpoint data..."
	@rm -rf ./data/datalake/* 2>/dev/null || true
	@rm -rf ./data/checkpoints/* 2>/dev/null || true
	@echo "🔧 Reinitializing directory structure..."
	@$(MAKE) init-volumes
	@echo "✅ Local data cleanup complete!"

# Clean only datalake data (keep checkpoints)
clean-datalake:
	@echo "🧹 CLEANING DATALAKE DATA"
	@echo "⚠️  This will permanently delete all processed data:"
	@echo "   • Clickstream parquet files"
	@echo "   • IoT sensor parquet files" 
	@echo "   • Aggregated analytics files"
	@echo "   ✅ Checkpoints will be preserved"
	@if [ -d "./data/datalake" ]; then \
		echo "📊 Current datalake size: $$(du -sh ./data/datalake 2>/dev/null | cut -f1)"; \
	fi
	@echo ""
	@read -p "Delete all datalake data? [y/N]: " confirm && [ "$$confirm" = "y" ]
	@echo "🗑️  Removing datalake data..."
	@rm -rf ./data/datalake/* 2>/dev/null || true
	@echo "🔧 Reinitializing datalake structure..."
	@./scripts/init-volumes.sh
	@echo "✅ Datalake cleanup complete!"

# Clean only checkpoint data (keep datalake)
clean-checkpoints:
	@echo "🧹 CLEANING CHECKPOINT DATA"
	@echo "⚠️  This will permanently delete streaming state:"
	@echo "   • Spark streaming offsets"
	@echo "   • Streaming job metadata"  
	@echo "   • Delta table logs"
	@echo "   ✅ Datalake files will be preserved"
	@if [ -d "./data/checkpoints" ]; then \
		echo "📊 Current checkpoint size: $$(du -sh ./data/checkpoints 2>/dev/null | cut -f1)"; \
	fi
	@echo ""
	@read -p "Delete all checkpoint data? [y/N]: " confirm && [ "$$confirm" = "y" ]
	@echo "🗑️  Removing checkpoint data..."
	@rm -rf ./data/checkpoints/* 2>/dev/null || true
	@echo "🔧 Reinitializing checkpoint structure..."
	@./scripts/init-volumes.sh
	@echo "✅ Checkpoint cleanup complete!"


# Show data usage statistics
data-stats:
	@echo "📊 LOCAL DATA STATISTICS"
	@echo "========================"
	@if [ -d "./data" ]; then \
		echo "📁 Directory sizes:"; \
		du -sh ./data/ ./data/datalake ./data/checkpoints 2>/dev/null || echo "No data directories found"; \
		echo ""; \
		echo "📄 File counts:"; \
		echo "   Datalake files: $$(find ./data/datalake -type f 2>/dev/null | wc -l)"; \
		echo "   Checkpoint files: $$(find ./data/checkpoints -type f 2>/dev/null | wc -l)"; \
		echo "   Total files: $$(find ./data -type f 2>/dev/null | wc -l)"; \
		echo ""; \
		echo "🗂️  Table breakdown:"; \
		for table in clickstream clickstream_agg iot; do \
			if [ -d "./data/datalake/tables/$$table" ]; then \
				size=$$(du -sh "./data/datalake/tables/$$table" 2>/dev/null | cut -f1); \
				files=$$(find "./data/datalake/tables/$$table" -name "*.parquet" 2>/dev/null | wc -l); \
				echo "   $$table: $$size ($$files parquet files)"; \
			fi; \
		done; \
	else \
		echo "❌ No data directory found. Run 'make up' first."; \
	fi
