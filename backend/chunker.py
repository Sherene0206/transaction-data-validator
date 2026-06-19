import zipfile
from pathlib import Path


class CSVChunker:
    """Handles splitting large CSV files into manageable chunks."""
    
    CHUNK_SIZE = 5000  # Maximum rows per chunk
    
    @staticmethod
    def create_chunks(csv_file_path, output_dir):
        """
        Split CSV file into chunks if it exceeds CHUNK_SIZE.
        Returns list of chunk file paths and whether chunks were created.
        """
        import pandas as pd
        
        # Read CSV
        df = pd.read_csv(csv_file_path)
        total_rows = len(df)
        
        # If file is small, no chunking needed
        if total_rows <= CSVChunker.CHUNK_SIZE:
            return [csv_file_path], False
        
        # Create chunks directory
        chunks_dir = Path(output_dir) / "chunks"
        chunks_dir.mkdir(exist_ok=True)
        
        chunk_files = []
        num_chunks = (total_rows + CSVChunker.CHUNK_SIZE - 1) // CSVChunker.CHUNK_SIZE
        
        # Create individual chunk files
        for i in range(num_chunks):
            start_idx = i * CSVChunker.CHUNK_SIZE
            end_idx = start_idx + CSVChunker.CHUNK_SIZE
            
            chunk_df = df.iloc[start_idx:end_idx]
            chunk_filename = chunks_dir / f"chunk_{i + 1}.csv"
            chunk_df.to_csv(chunk_filename, index=False)
            chunk_files.append(chunk_filename)
        
        return chunk_files, True
    
    @staticmethod
    def create_zip(chunk_files, output_dir, timestamp):
        """Create a ZIP file containing all chunks."""
        zip_path = Path(output_dir) / f"chunks_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for chunk_file in chunk_files:
                # Add file with just the filename (not full path)
                zipf.write(chunk_file, arcname=chunk_file.name)
        
        return zip_path
