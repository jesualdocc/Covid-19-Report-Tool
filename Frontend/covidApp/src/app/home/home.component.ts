import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { DataService } from '../services/data.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  title:string = "Covid Report";

  constructor(private dataService:DataService, private router:Router) {
    this.dataService.changePageTitle(this.title);

  }

  ngOnInit(): void {
    this.router.navigate(['/login']);

  }

}
