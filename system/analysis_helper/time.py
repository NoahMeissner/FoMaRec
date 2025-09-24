"""This module provides functions to analyze time taken for conversations."""
import numpy as np
import json
from datetime import datetime
from analysis_helper.load_dataset import get_file_path
from foodrec.config.structure.dataset_enum import ModelEnum

def calc_time(persona_id: int, query: str, model: ModelEnum, path = None):
    """Calculate the time difference between the first and last message in seconds"""
    filepath = get_file_path(Path=path, query=query, persona_id=persona_id, model=model)
    if filepath is None:
        return 0
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            if not lines:
                return 0
            first_obj = json.loads(lines[0])
            last_obj = json.loads(lines[-1])
            time_first = first_obj.get("ts")
            time_last = last_obj.get("ts")
            fmt = "%Y-%m-%dT%H:%M:%S%z"
            dt1 = datetime.strptime(time_first.replace("Z", "+00:00"), fmt)
            dt2 = datetime.strptime(time_last.replace("Z", "+00:00"), fmt)
            time = (dt2 - dt1).total_seconds()
            return time
    except Exception as e:
        print(e)
        return 0

def calc_mean_time(df, paths, model_name: ModelEnum):
    """Calculate the mean time for different paths"""
    def calc_median_time(df, model:ModelEnum, path):
        ls = []
        for _, row in df.iterrows():
            persona_id = row["id"]
            query = row["query"]
            ls.append(calc_time(persona_id=persona_id, query=query, model=model, path=path))
        return np.mean(ls)
    print("Mean Time No Biase:", calc_median_time(df, model_name, paths['PATH_NO_BIASE']))
    print("Mean Time System Biase:", calc_median_time(df, model_name, paths['PATH_SYSTEM_BIASE']))
    print("Mean Time Search Biase:", calc_median_time(df, model_name, paths['PATH_SEARCH_BIASE']))
    print("Mean Both Biase:", calc_median_time(df, model_name, paths['PATH_BOTH']))
