#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tinydb import Query, where

def safe_load_settings(field, settings):
	if field in settings:
		return True, settings[field], "Load {} : {}".format(field, settings[field])
	return False, None, "Unable to load {}".format(field) 

def return_elements(database, owner, entity="job"):
	query = Query()
	items = database.search((where('entity') == entity) & (where('owner') == owner)) 
	return items

def save_element(database, data, owner, entity="job"):
	data['entity'] = entity
	data['owner'] = str(owner)
	database.insert( data )

def delete_job(database, name, owner):
	database.remove((where('entity') == "job") & (where('owner') == owner) & (where('name') == name))

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def fix_days(days_args):
	if type(days_args[0]) == int:
		return days_args
	return [ days.index(day.strip()) for day in days_args.split(',') ]