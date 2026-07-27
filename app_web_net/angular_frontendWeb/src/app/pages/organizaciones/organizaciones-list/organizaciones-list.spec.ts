import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OrganizacionesList } from './organizaciones-list';

describe('OrganizacionesList', () => {
  let component: OrganizacionesList;
  let fixture: ComponentFixture<OrganizacionesList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OrganizacionesList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OrganizacionesList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
