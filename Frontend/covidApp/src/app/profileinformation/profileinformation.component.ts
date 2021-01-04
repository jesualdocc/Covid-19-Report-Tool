import { LoginService } from 'src/app/login/login.service';
import { DataService } from 'src/app/services/data.service';
import { Component, OnInit } from '@angular/core';
import { Users } from 'src/app/registration/Users';
import { Router } from '@angular/router';
import { usStates } from '../services/States';


@Component({
  selector: 'app-profileinformation',
  templateUrl: './profileinformation.component.html',
  styleUrls: ['./profileinformation.component.css']
})
export class ProfileinformationComponent implements OnInit {

  states = usStates;
  counties = [];
  model = new Users();
  submitted = false;
  submissionMessage = '';
  errorMessage = false;
  loading:boolean = false;
  countyListEnable = true;

  constructor(private dataService:DataService, private router:Router, private loginService:LoginService) { }

  ngOnInit(): void {
    this.getUser();
    this.getStateCounties(this.model.state, 0)

  }

  getStateCounties(state:string, change:number){
    //0 - No change, 1- Change
    this.loading = true;

    if(change){
      this.countyListEnable = false;
      this.counties = []
    }

    this.dataService.getCounties({'state':state}).subscribe(data=>{
      if(data.status == 200){

        var result = data['body'].data
        for(var i of result){
          this.counties.push(i)
        }

        this.counties.sort()
        this.loading = false;
        this.countyListEnable = true;
      }

    })
  }

  getUser(){
      var data = this.loginService.user;

      this.model.id = data['id'];
      this.model.firstName = data['firstName'];
      this.model.lastName = data['lastName'];
      this.model.userName = data['userName'];
      this.model.email = data['email'];
      this.model.password = data['password'];
      this.model.county = data['county'];
      this.model.state = data['state'];
  }

  onSubmit(){

    this.sendData();


  }

  cancel(){
    this.router.navigate(['/dashboard']);
  }

  sendData(){

    this.dataService.updateUser(this.model, 'profile').subscribe(result=>{
      if(result.status == 201){
        this.errorMessage = false;
        this.submitted = true;
        this.submissionMessage = '';

        this.loginService.logout();
        alert("User Info Updated")
      }

   },
   err=>{
        this.errorMessage = true;
        this.submissionMessage = "An error occurred!Try Again...";
   }
   );
  }

}

