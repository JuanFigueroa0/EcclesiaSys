import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RolesList } from './roles-list';

describe('RolesList', () => {
  let component: RolesList;
  let fixture: ComponentFixture<RolesList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RolesList],
    }).compileComponents();

    fixture = TestBed.createComponent(RolesList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
