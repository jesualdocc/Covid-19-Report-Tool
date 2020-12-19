import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { LocalStorage, LocalStorageService } from 'ngx-webstorage';
import { ILogin } from './login';
import { LoginService } from './login.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {

  formGroup:FormGroup | undefined;
  submissionMessage: string;

  constructor(private loginService:LoginService, private router:Router, private localSt:LocalStorageService){

  }


  ngOnInit(): void {
    this.initForm();
  }

  initForm(){
    this.formGroup = new FormGroup({
      userName: new FormControl("", [Validators.required, Validators.minLength(5)]),
      password: new FormControl("", [Validators.required, Validators.minLength(6)])
    })
  }

  loginProcess(){

    if(this.formGroup?.valid){
      this.loginService.loginHandler(this.formGroup.value).subscribe(data=>{

        if(data.status == 201){
          this.loginService.user = data['body'].user;

          this.localSt.store('token', data['body'].token);

          this.loginService.isLoggedIn = true;
          this.submissionMessage = '';
          this.router.navigate(['/dashboard']);

        }

      }, err=> {

        if(err.status == 401){
          this.submissionMessage = "Username or Password is incorrect";
        }
        else{
          this.submissionMessage = "An error occurred!Try Again...";
          this.loginService.logout();
        }

      }

        );
    }
  }

  registration():void{
    this.router.navigate(['/registration']);
  }

}
