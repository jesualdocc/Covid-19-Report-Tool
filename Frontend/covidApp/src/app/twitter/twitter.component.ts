import { Component, OnInit } from '@angular/core';
import { DataService } from '../services/data.service';

@Component({
  selector: 'app-twitter',
  templateUrl: './twitter.component.html',
  styleUrls: ['./twitter.component.css']
})
export class TwitterComponent implements OnInit {
  tweetsList = [];
  allTweetsLoaded = false;

  constructor(private dataService:DataService) {

    this.dataService.changePageTitle("Twitter Feed");
    this.getData()
   }

  ngOnInit(): void {
  }

  getData(){

    this.dataService.getTweets().subscribe(result =>{
      var data = result['body'].tweets;
      for(var tweets of data){

        this.tweetsList.push(tweets);

      }

      this.allTweetsLoaded = true;

    },
    err=>{
      this.allTweetsLoaded = false;

    })

  }
}
