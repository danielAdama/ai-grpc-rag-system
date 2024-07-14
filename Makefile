download_spacy_packages:
	@echo "Downloading spacy data..."
	python3 -m spacy download en_core_web_sm

start_server:
	@echo "Starting Server..."
	python3 src/server/pdf_service.py