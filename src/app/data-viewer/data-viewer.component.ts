import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DataService } from '../services/data.service';
import { DataRecord } from '../models/data.model';

@Component({
  selector: 'app-data-viewer',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="data-viewer-container">
      <h2>📊 Données Capturées</h2>
      
      <div class="controls">
        <button (click)="loadData()" class="btn btn-primary">🔄 Actualiser</button>
        <input type="number" [(ngModel)]="userId" placeholder="ID Utilisateur" class="user-id-input">
      </div>
      
      <div class="data-list">
        <div *ngFor="let record of dataRecords" class="data-card">
          <div class="card-header">
            <h3>ID: {{ record.id }} - {{ record.timestamp | date:'short' }}</h3>
            <span class="movement-badge" [class.active]="record.movementDetected">
              {{ record.movementDetected ? '🏃 Mouvement' : '⏸️ Aucun' }}
            </span>
          </div>
          
          <div class="card-content">
            <div class="image-preview" *ngIf="record.imageData">
              <img [src]="record.imageData" alt="Capture" class="preview-image">
            </div>
            
            <div class="video-info" *ngIf="record.videoUrl">
              <p>🎥 Vidéo: <a [href]="record.videoUrl" target="_blank">{{ record.videoUrl }}</a></p>
            </div>
            
            <div class="json-data" *ngIf="record.jsonData">
              <h4>📝 Données JSON:</h4>
              <pre>{{ record.jsonData | json }}</pre>
            </div>
          </div>
        </div>
        
        <div *ngIf="dataRecords.length === 0" class="no-data">
          <p>📭 Aucune donnée capturée pour l'utilisateur {{ userId }}</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .data-viewer-container {
      padding: 20px;
      max-width: 1200px;
      margin: 0 auto;
    }
    
    .controls {
      display: flex;
      gap: 10px;
      margin-bottom: 20px;
      align-items: center;
    }
    
    .user-id-input {
      padding: 8px 12px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 14px;
    }
    
    .btn {
      padding: 8px 16px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
    }
    
    .btn-primary {
      background-color: #007bff;
      color: white;
    }
    
    .data-list {
      display: grid;
      gap: 20px;
    }
    
    .data-card {
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 16px;
      background-color: #f9f9f9;
    }
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }
    
    .movement-badge {
      padding: 4px 8px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: bold;
    }
    
    .movement-badge.active {
      background-color: #28a745;
      color: white;
    }
    
    .preview-image {
      max-width: 100%;
      max-height: 300px;
      border-radius: 4px;
    }
    
    .json-data pre {
      background-color: #f1f1f1;
      padding: 10px;
      border-radius: 4px;
      overflow-x: auto;
    }
    
    .no-data {
      text-align: center;
      padding: 40px;
      color: #666;
    }
  `]
})
export class DataViewerComponent implements OnInit {
  dataRecords: DataRecord[] = [];
  userId = 1; // Default user ID
  
  constructor(private dataService: DataService) {}
  
  ngOnInit(): void {
    this.loadData();
  }
  
  loadData(): void {
    this.dataService.getDataRecordsByUserId(this.userId).subscribe({
      next: (records) => {
        this.dataRecords = records;
        console.log('📋 Loaded data records:', records);
      },
      error: (err) => {
        console.error('❌ Error loading data records:', err);
        // Fallback to local storage if backend is not available
        this.dataService.getDataRecordsByUserIdLocal(this.userId).subscribe({
          next: (localRecords) => {
            this.dataRecords = localRecords;
            console.log('📋 Loaded data records from local storage:', localRecords);
          },
          error: (localErr) => {
            console.error('❌ Error loading local data records:', localErr);
          }
        });
      }
    });
  }
}