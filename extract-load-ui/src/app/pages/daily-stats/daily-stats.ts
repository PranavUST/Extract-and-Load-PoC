import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { DateAdapter, MAT_DATE_FORMATS, MAT_DATE_LOCALE } from '@angular/material/core';
import { MomentDateAdapter, MAT_MOMENT_DATE_ADAPTER_OPTIONS } from '@angular/material-moment-adapter';
import moment from 'moment'; // Change to default import

// Add custom date formats
export const MY_FORMATS = {
  parse: {
    dateInput: 'DD/MM/YYYY',
  },
  display: {
    dateInput: 'DD/MM/YYYY',
    monthYearLabel: 'MMMM YYYY',
    dateA11yLabel: 'LL',
    monthYearA11yLabel: 'MMMM YYYY',
  },
};

interface PipelineStats {
  stat_date: Date;
  total_records_fetched: number;
  total_records_inserted: number;
  total_error_count: number;
  last_status: string;
  last_run_timestamp: Date | null;  // Allow null value
}

@Component({
  selector: 'app-daily-stats',
  standalone: true,
  templateUrl: './daily-stats.html',
  styleUrls: ['./daily-stats.scss'],
  imports: [
    CommonModule, 
    RouterLink, 
    FormsModule,
    MatButtonModule, 
    MatIconModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatCardModule,
    MatTableModule,
    MatProgressSpinnerModule,
    HttpClientModule
  ],
  providers: [
    { provide: MAT_DATE_LOCALE, useValue: 'en-GB' },
    {
      provide: DateAdapter,
      useClass: MomentDateAdapter,
      deps: [MAT_DATE_LOCALE, MAT_MOMENT_DATE_ADAPTER_OPTIONS]
    },
    { 
      provide: MAT_MOMENT_DATE_ADAPTER_OPTIONS,
      useValue: { useUtc: true }
    },
    { provide: MAT_DATE_FORMATS, useValue: MY_FORMATS },
  ]
})
export class DailyStats implements OnInit {
  selectedDate: moment.Moment;
  stats: PipelineStats | null = null;
  loading = false;
  error: string | null = null;
  displayedColumns: string[] = [
    'total_records_fetched',
    'total_records_inserted',
    'total_error_count',
    'last_status',
    'last_run_timestamp'
  ];

  constructor(
    private http: HttpClient,
    private dateAdapter: DateAdapter<moment.Moment>
  ) {
    this.dateAdapter.setLocale('en-GB');
    this.selectedDate = moment().startOf('day');
  }

  ngOnInit() {
    this.fetchStats();
  }

  onDateChange(event: any) {
    if (event.value) {
      this.selectedDate = moment(event.value).startOf('day');
      this.fetchStats();
    }
  }

  fetchStats() {
    this.loading = true;
    this.error = null;
    this.stats = null;

    const formattedDate = this.selectedDate.format('YYYY-MM-DD');
    
    this.http.get<any>(`http://localhost:5000/pipeline-stats/${formattedDate}`).subscribe({
      next: (data) => {
        if (data) {
          this.stats = {
            stat_date: new Date(data.stat_date),
            total_records_fetched: data.total_records_fetched ?? 0,
            total_records_inserted: data.total_records_inserted ?? 0,
            total_error_count: data.total_error_count ?? 0,
            last_status: data.last_status || '-',
            last_run_timestamp: data.last_run_timestamp ? new Date(data.last_run_timestamp) : null
          };
        } else {
          this.error = 'No data available for selected date';
        }
        this.loading = false;
      },
      error: (err) => {
        console.error('Error fetching stats:', err);
        this.error = 'Failed to fetch stats for the selected date';
        this.loading = false;
      }
    });
  }
}
