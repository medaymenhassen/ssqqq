import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DataService } from '../services/data.service';
import { DataRecord } from '../models/data.model';

@Component({
  selector: 'app-data-viewer',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './data-viewer.component.html',
  styleUrls: ['./data-viewer.component.scss']
})
export class DataViewerComponent implements OnInit {
  dataRecords: DataRecord[] = [];
  userId = 1; // Default user ID
  loading = false;
  error: string | null = null;
  
  constructor(private dataService: DataService) {}  
  
  ngOnInit(): void {
    this.loadData();
  }
  
  loadData(): void {
    this.loading = true;
    this.error = null;
    
    this.dataService.getDataRecordsByUserId(this.userId).subscribe({
      next: (records) => {
        this.dataRecords = records;
        this.loading = false;
        console.log('📋 Loaded data records:', records);
      },
      error: (err) => {
        console.error('❌ Error loading data records:', err);
        this.error = 'Failed to load data records';
        this.loading = false;
        
        // Fallback to local storage if backend is not available
        this.dataService.getDataRecordsByUserIdLocal(this.userId).subscribe({
          next: (localRecords) => {
            this.dataRecords = localRecords;
            console.log('📋 Loaded data records from local storage:', localRecords);
          },
          error: (localErr) => {
            console.error('❌ Error loading local data records:', localErr);
            this.error = 'Failed to load data records from server or local storage';
          }
        });
      }
    });
  }

  downloadData(record: DataRecord): void {
    // Implementation for downloading data
    console.log('📥 Downloading data for record:', record.id);
    
    // Create a simple text representation of the data
    const dataStr = `ID: ${record.id}
Timestamp: ${record.timestamp}
Movement Detected: ${record.movementDetected}
${record.position ? `Position: (${record.position.x}, ${record.position.y})` : ''}
${record.velocity ? `Velocity: ${record.velocity}` : ''}
${record.direction ? `Direction: ${record.direction}` : ''}
${record.confidence ? `Confidence: ${record.confidence}` : ''}`;

    // Create and download a text file
    const blob = new Blob([dataStr], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `data-record-${record.id}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  deleteRecord(id: number | undefined): void {
    if (id === undefined) return;
    
    console.log('🗑️ Deleting record with ID:', id);
    
    // Remove from local array
    this.dataRecords = this.dataRecords.filter(record => record.id !== id);
    
    // In a real application, you would also call a service to delete from backend
    // this.dataService.deleteRecord(id).subscribe(...);
  }
}