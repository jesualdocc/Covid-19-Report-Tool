import { Component, OnInit } from '@angular/core';
import { Users } from '../registration/Users';
import { DataService } from '../services/data.service';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.css']
})
export class SettingsComponent implements OnInit {
  title:string ="Account Settings";
  model = new Users();
  submitted = false;
  submissionMessage = '';
  checkCurrentP:string; //current password
  checkMatch:string = "";

  //Property that get checks in realtime
  get passwordMatch():boolean{

    return this.model.password == this.checkMatch ? true:false;

  }

  constructor(private dataService:DataService) {
    this.dataService.changePageTitle(this.title);
   }

  ngOnInit(): void {
  }



  onSubmit(){

  }
}
