import { Component } from '@angular/core';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { DataService } from './services/data.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'covidApp';
  showHeader = false;
  showSidebar = false;
  showFooter = false;
  activeMenu = false;
  isGlobeView = false;

  constructor(private router: Router, private activatedRoute: ActivatedRoute,
    private dataService:DataService){}

  ngOnInit() {
    this.dataService.currentSidebarStatus.subscribe(s=> this.activeMenu = s);
    this.dataService.currentView.subscribe(s => this.isGlobeView = s);

    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.showHeader = this.activatedRoute.firstChild.snapshot.data.showHeader !== false;
        this.showSidebar = this.activatedRoute.firstChild.snapshot.data.showSidebar !== false;
        this.showFooter = this.activatedRoute.firstChild.snapshot.data.showFooter !== false;
      }
    });
  }

}

