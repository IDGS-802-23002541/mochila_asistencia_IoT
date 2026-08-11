import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute } from '@angular/router';

import { MisProductos } from './productos';

describe('MisProductos', () => {
  let component: MisProductos;
  let fixture: ComponentFixture<MisProductos>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MisProductos],
      providers: [
        {
          provide: ActivatedRoute,
          useValue: { snapshot: { paramMap: { get: () => '1' } } },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MisProductos);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});