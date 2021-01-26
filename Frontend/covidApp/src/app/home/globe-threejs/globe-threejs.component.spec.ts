import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GlobeThreejsComponent } from './globe-threejs.component';

describe('GlobeThreejsComponent', () => {
  let component: GlobeThreejsComponent;
  let fixture: ComponentFixture<GlobeThreejsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GlobeThreejsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GlobeThreejsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
