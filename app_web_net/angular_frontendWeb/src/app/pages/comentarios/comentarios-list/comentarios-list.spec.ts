import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ComentariosList } from './comentarios-list';

describe('ComentariosList', () => {
  let component: ComentariosList;
  let fixture: ComponentFixture<ComentariosList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ComentariosList],
    }).compileComponents();

    fixture = TestBed.createComponent(ComentariosList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
