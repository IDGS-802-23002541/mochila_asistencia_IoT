import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OrganizacionDetalle } from './organizacion-detalle';

describe('OrganizacionDetalle', () => {
  let component: OrganizacionDetalle;
  let fixture: ComponentFixture<OrganizacionDetalle>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OrganizacionDetalle]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OrganizacionDetalle);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
