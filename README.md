# Snapshot API
A simple flask web server where user can easily create snapshot for their HDFS directory.

## CREATE

**Create a new snapshot under specified directory.**

| **key**          | **value**               |
| ---------------- | ----------------------- |
| **route**        | /snapshot/action/create |
| **method**       | POST                    |
| **content-type** | form-data               |
| **parameters**   | USER,PATH,SNAPSHOTNAME  |

**Requests:**
curl -X POST -d "USER=employee_code&PATH=hdfs://nameservice/directory" http://127.0.0.1:5000/snapshot/action/create

**Success Return:**

```json
{"msg": "Create Snapshot Successfully.",
"code": 200,
"user": "employee_code",
"path": "path needs to create snapshot",
"snapshot_name": "snapshot name set up by user, auto created if None is specified.| auto created with the snapshot name specified",
"action": "CREATE"}
```

**Failure Return**

```json
{"msg": "Failed to create snapshot, total snapshot count might be over 7.",
"code": 403,
"user": "employee_code",
"path": "path needs to create snapshot",
"snapshot_name": "snapshot name set up by user, auto created if None is specified.| auto created with the snapshot name specified",
"action": "CREATE"}
```

## DELETE

**Delete an existed snapshot.**

| **key**          | **value**                |
| ---------------- | ------------------------ |
| **route**        | /snapshot/action/delete  |
| **method**       | POST                     |
| **content-type** | form-data                |
| **parameters**   | USER, PATH, SNAPSHOTNAME |

**Requests:**
curl -X POST -d "USER=employee_code&PATH=hdfs://nameservice/directory&SNAPSHOTNAME=snapshot_name" http://127.0.0.1:5000/snapshot/action/delete

**Success Return:**

```json
{"msg": "Delete Snapshot Successfully.",
"code": 200,
"user": "employee_code",
"path": "path needs to delete snapshot",
"snapshot_name": "snapshot name has to be specified.",
"action": "DELETE"}
```

**Failure Return**

```json
{"msg": "Failed to delete snapshot, snapshot might not existed.",
"code": 403,
"user": "employee_code",
"path": "path needs to delete snapshot",
"snapshot_name": "snapshot name has to be specified.",
"action": "DELETE"}
```

## RENAME

**Rename an existed snapshot with new name.**

| **key**          | **value**                                 |
| ---------------- | ----------------------------------------- |
| **route**        | /snapshot/action/rename                   |
| **method**       | POST                                      |
| **content-type** | form-data                                 |
| **parameters**   | USER, PATH, OLDSNAPSHOTNAME, SNAPSHOTNAME |

PS: OLDSNAPSHOTNAME: current snapshot name we want to change，SNAPSHOTNAME: new snapshot name。

**Requests:**
curl -X POST -d "USER=employee_code&PATH=hdfs://nameservice/directory&OLDSNAPSHOTNAME=old_snapshot_name&SNAPSHOTNAME=new_snapshot_name" http://127.0.0.1:5000/snapshot/action/rename

**Success Return:**

```json
{"msg": "Delete Snapshot Successfully.",
"code": 200,
"user": "employee_code",
"path": "path needs to rename snapshot",
"old_snapshot_name": "old_snapshot_name",
"snapshot_name": "new_snapshot_name",
"action": "RENAME"}
```

**Failure Return**

```json
{"msg": "Failed to rename snapshot.",
"code": 403,
"user": "employee_code",
"path": "path needs to rename snapshot",
"old_snapshot_name": "old_snapshot_name",
"snapshot_name": "new_snapshot_name",
"action": "RENAME"}
```

## RECOVER

**Recover files from a snapshot to a specified directory.**

| **key**          | **value**                          |
| ---------------- | ---------------------------------- |
| **route**        | /snapshot/action/recover           |
| **method**       | POST                               |
| **content-type** | form-data                          |
| **parameters**   | USER, PATH, SNAPSHOTNAME, FILENAME |

**Requests:**
curl -X POST -d "USER=employee_code&PATH=hdfs://nameservice/directory&SNAPSHOTNAME=recover_from_this_snapshot&FILENAME=filename_to_be_recovered" http://127.0.0.1:5000/snapshot/action/recover

**Success Return:**

```json
{"msg": "Recover Snapshot Successfully.",
"code": 200,
"user": "employee_code",
"path": "file/directory would be recovered to this path.",
"snapshot_name": "recover_from_this_snapshot",
"filename": "filename needs to be recovered, system would recovered all files under snapshot dir if no filename is specified.",
"action": "RECOVER"}
```

**Failure Return**

```json
{"msg": "Failed to restore snapshot!",
"code": 403,
"user": "employee_code",
"path": "file/directory would be recovered to this path.",
"snapshot_name": "recover_from_this_snapshot",
"filename": "filename needs to be recovered, system would recovered all files under snapshot dir if no filename is specified.",
"action": "RECOVER"}
```

## DISPLAY

**Display all snapshots of an employee.**

| **key**          | **value**                   |
| ---------------- | --------------------------- |
| **route**        | /snapshot/display/all       |
| **method**       | POST                        |
| **content-type** | form-data                   |
| **parameters**   | USER, page_index, page_size |

**Requests:**
curl -X POST -d "USER=employee_code&page_size=25&page_index=1" http://127.0.0.1:5000/snapshot/display/all

**Return:**

```json
{"msg": "Dispaly Snapshot of user [{用户工号}] Successfully",
"code": 200,
"user": "employee_code",
"page_index": "page index",
"page_size": "page size",
"action": "RECOVER"}
```

## DIFFER

**Show difference between two snapshot.**

| **key**          | **value**                                 |
| ---------------- | ----------------------------------------- |
| **route**        | /snapshot/display/differ                  |
| **method**       | POST                                      |
| **content-type** | form-data                                 |
| **parameters**   | USER, PATH, OLDSNAPSHOTNAME, SNAPSHOTNAME |

**Requests：**
curl -X POST -d "USER=employee_code&PATH=hdfs://nameservice/directory&OLDSNAPSHOTNAME=current_snapshot_name&SNAPSHOTNAME=another_snapshot_name" http://127.0.0.1:5000/snapshot/action/differ

**Return:**

```json
{"msg": "Show Difference between Snapshot Successfully.",
"code": 200,
"user": "employee_code",
"old_snapshot_name": "current snapshot name",
"snapshot_name": "another snapshot name",
"action": "DIFFER"}
```