import { baseTestingUrl, baseUrl } from './../../environments/environment';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ILogin } from './login';

import { LoginService } from './login.service';
import { HttpHeaders, HttpResponse } from '@angular/common/http';

fdescribe('LoginService', () => {
  let service: LoginService;
  let httpMock:HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports:[HttpClientTestingModule],
      providers:[LoginService]
    });
    service = TestBed.inject(LoginService);
    httpMock = TestBed.inject(HttpTestingController);

  });

  fit('should post login credentials along with headers for authentication', () => {
    const dummyPosts = [
      {
            userName: "A1",
            password:"a1234a"
        },
        {
          userName: "A2",
          password:"b1234a"
      },
      {
        userName: "A3",
        password:""
    }
];


const request = httpMock.expectOne( `${baseTestingUrl}/getall`);

expect(request.request.method).toBe('GET');
expect(request.request.responseType).toBe('json');
request.flush(dummyPosts);
console.log('Run2');



  });

  afterEach(()=>{
    httpMock.verify();
  });

});
