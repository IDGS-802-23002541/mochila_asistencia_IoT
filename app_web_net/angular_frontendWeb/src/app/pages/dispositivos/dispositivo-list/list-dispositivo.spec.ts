import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListDispositivo } from './list-dispositivo';

describe('ListDispositivo', () => {
  let component: ListDispositivo;
  let fixture: ComponentFixture<ListDispositivo>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListDispositivo],
    }).compileComponents();

    fixture = TestBed.createComponent(ListDispositivo);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
