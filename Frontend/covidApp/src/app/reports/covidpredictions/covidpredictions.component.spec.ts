import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CovidpredictionsComponent } from './covidpredictions.component';

describe('CovidpredictionsComponent', () => {
  let component: CovidpredictionsComponent;
  let fixture: ComponentFixture<CovidpredictionsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CovidpredictionsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CovidpredictionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
