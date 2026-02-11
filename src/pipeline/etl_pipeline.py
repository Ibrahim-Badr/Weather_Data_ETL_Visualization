"""
ETL Pipeline with Queue (processing order) + LinkedList (history tracking).
"""
from typing import List, Optional
from datetime import datetime
import time


from ..extractors.interface import IDataExtractor
from ..transformers.interface import IDataTransformer
from ..loaders.interface import IDataLoader


# ✅ Import BOTH data structures
from ..structures.queue import Queue
from ..structures.linked_list import LinkedList



class ProcessingRecord:
    """Record of a single processing event (for LinkedList)."""
    def __init__(self, station_id: str, record_count: int, timestamp: datetime, status: str):
        self.station_id = station_id
        self.record_count = record_count
        self.timestamp = timestamp
        self.status = status  # "success", "failed", "skipped"
    
    def __repr__(self):
        return (f"ProcessingRecord(station={self.station_id}, "
                f"records={self.record_count}, status={self.status})")



class ETLPipeline:
    """
    ETL Pipeline with dual data structures:
    - Queue: Manages station processing order (FIFO)
    - LinkedList: Tracks processing history chronologically
    """
    
    def __init__(
        self,
        extractor: IDataExtractor,
        transformer: IDataTransformer,
        loader: IDataLoader
    ):
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader
        
        # ✅ Queue: Stations waiting to be processed (FIFO)
        self.processing_queue = Queue[str]()
        
        # ✅ LinkedList: History of all processing events
        self.processing_history = LinkedList[ProcessingRecord]()
        
        # Statistics
        self.stats = {
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'raw_records_extracted': 0,
            'valid_records_cleaned': 0,
            'records_saved': 0,
            'stations_processed': 0,
            'stations_failed': 0
        }
    
    def run(
        self,
        station_ids: Optional[List[str]] = None,
        limit_per_station: int = 100
    ) -> dict:
        """
        Run ETL pipeline using:
        - Queue to process stations in order
        - LinkedList to track processing history
        """
        print("\n" + "="*70)
        print("🚀 Starting ETL Pipeline")
        print("   📋 Queue: Manages processing order (FIFO)")
        print("   🔗 LinkedList: Tracks processing history")
        print("="*70)
        
        self.stats['start_time'] = datetime.now()
        start_time = time.time()
        
        try:
            # Get available stations
            all_stations = self.extractor.get_available_stations()
            
            # Filter by station_ids if provided
            if station_ids:
                stations = [s for s in all_stations if s['station_id'] in station_ids]
            else:
                stations = all_stations[:10]  # Limit to 10 for demo
            
            # ✅ QUEUE: Add all stations to processing queue
            print(f"\n📋 Adding {len(stations)} stations to Queue...")
            for station in stations:
                self.processing_queue.enqueue(station['station_id'])
                print(f"   → Enqueued: {station['station_id']}")
            
            print(f"\n✓ Queue initialized with {self.processing_queue.size()} stations")
            
            # ✅ QUEUE: Process stations in FIFO order
            print("\n🔄 Processing stations from Queue (FIFO)...\n")
            
            all_clean_data = []
            
            while not self.processing_queue.is_empty():
                # ✅ FIX 1: Handle Optional[str] from dequeue
                station_id = self.processing_queue.dequeue()
                
                # Type guard: skip if None
                if station_id is None:
                    continue
                
                remaining = self.processing_queue.size()
                
                print(f"📍 Processing station: {station_id} (Queue remaining: {remaining})")
                
                # Find station info
                station_info = next((s for s in stations if s['station_id'] == station_id), None)
                
                if not station_info:
                    print(f"   ⚠ Station {station_id} not found, skipping...")
                    
                    # ✅ LINKED LIST: Record skip event
                    self.processing_history.append(ProcessingRecord(
                        station_id=station_id,
                        record_count=0,
                        timestamp=datetime.now(),
                        status="skipped"
                    ))
                    continue
                
                try:
                    # ✅ FIX 2: Use public extract() method instead of private _extract_station_data
                    # Extract data for this single station
                    raw_data = self.extractor.extract(
                        station_ids=[station_id], 
                        limit=limit_per_station
                    )
                    
                    if not raw_data:
                        print("   ⚠ No data extracted")
                        
                        # ✅ LINKED LIST: Record no-data event
                        self.processing_history.append(ProcessingRecord(
                            station_id=station_id,
                            record_count=0,
                            timestamp=datetime.now(),
                            status="no_data"
                        ))
                        continue
                    
                    # Transform
                    clean_data = self.transformer.transform(raw_data)
                    
                    if clean_data:
                        # Load
                        self.loader.save(clean_data)
                        all_clean_data.extend(clean_data)
                        
                        print(f"   ✓ Saved {len(clean_data)} records")
                        
                        # ✅ LINKED LIST: Record success event
                        self.processing_history.append(ProcessingRecord(
                            station_id=station_id,
                            record_count=len(clean_data),
                            timestamp=datetime.now(),
                            status="success"
                        ))
                        
                        self.stats['stations_processed'] += 1
                        self.stats['records_saved'] += len(clean_data)
                    
                except (ValueError, KeyError, RuntimeError) as e:
                    print(f"   ✗ Error: {e}")
                    
                    # ✅ LINKED LIST: Record failure event
                    self.processing_history.append(ProcessingRecord(
                        station_id=station_id,
                        record_count=0,
                        timestamp=datetime.now(),
                        status="failed"
                    ))
                    
                    self.stats['stations_failed'] += 1
            
            # Calculate duration
            self.stats['end_time'] = datetime.now()
            self.stats['duration_seconds'] = round(time.time() - start_time, 2)
            
            # Print summary
            self._print_summary()
            
            return self.stats
            
        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            self.stats['end_time'] = datetime.now()
            self.stats['duration_seconds'] = round(time.time() - start_time, 2)
            raise
    
    def _print_summary(self):
        """Print pipeline execution summary."""
        print("\n" + "="*70)
        print("✅ ETL Pipeline Completed")
        print("="*70)
        print(f"⏱  Duration: {self.stats['duration_seconds']} seconds")
        print(f"💾 Records saved: {self.stats['records_saved']}")
        print(f"🏢 Stations processed: {self.stats['stations_processed']}")
        print(f"❌ Stations failed: {self.stats['stations_failed']}")
        
        # ✅ Show LinkedList history
        self._print_processing_history()
        
        print("="*70 + "\n")
    
    def _print_processing_history(self):
        """Display processing history from LinkedList."""
        print("\n🔗 Processing History (LinkedList):")
        print("-" * 70)
        
        history = self.processing_history.to_list()
        
        if not history:
            print("   (No history recorded)")
            return
        
        for i, record in enumerate(history, 1):
            time_str = record.timestamp.strftime('%H:%M:%S')
            status_emoji = {
                'success': '✓',
                'failed': '✗',
                'skipped': '⊘',
                'no_data': '⚠'
            }.get(record.status, '?')
            
            print(f"   {i}. [{time_str}] {status_emoji} "
                  f"Station {record.station_id}: "
                  f"{record.status} ({record.record_count} records)")
        
        print("-" * 70)
        print(f"Total events tracked: {len(history)}")
    
    # ✅ PUBLIC METHODS: Access data structures
    
    def get_processing_history(self) -> List[ProcessingRecord]:
        """
        Get complete processing history from LinkedList.
        Maintains chronological order of events.
        """
        return self.processing_history.to_list()
    
    def get_queue_status(self) -> dict:
        """
        Get current queue status.
        Useful for monitoring during long-running pipelines.
        """
        return {
            'remaining_stations': self.processing_queue.size(),
            'is_empty': self.processing_queue.is_empty(),
            'next_station': self.processing_queue.peek()
        }
    
    def get_stats(self) -> dict:
        """Get pipeline statistics."""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset pipeline statistics and clear history."""
        self.stats = {
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'raw_records_extracted': 0,
            'valid_records_cleaned': 0,
            'records_saved': 0,
            'stations_processed': 0,
            'stations_failed': 0
        }
        
        # Clear history but keep structure
        self.processing_history = LinkedList[ProcessingRecord]()
