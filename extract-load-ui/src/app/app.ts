import { Component } from '@angular/core';
import { RouterOutlet, RouterModule, Router, NavigationEnd } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { Footer } from './layout/footer/footer';
import { CommonModule } from '@angular/common';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  imports: [CommonModule, RouterOutlet, RouterModule, MatToolbarModule, MatButtonModule, Footer],
  templateUrl: './app.html',
  styleUrls: ['./app.scss']
})
export class App {
  public title = 'extract-load-ui';
  public isLoginPage = false;

  constructor(private router: Router) {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.isLoginPage = event.urlAfterRedirects === '/login';
    });
  }
}