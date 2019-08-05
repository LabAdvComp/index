Index
===
![version](https://img.shields.io/badge/version-0.0.1-orange.svg?style=flat) [![Apache license](http://img.shields.io/badge/license-Apache-blue.svg?style=flat)](LICENSE) [![Travis](https://travis-ci.org/LabAdvComp/index.svg?branch=master)](https://travis-ci.org/LabAdvComp/index)

Index is a prototype data indexing and tracking client. It is intended to
provide a simple means of interactively investigating
[indexd](https://github.com/LabAdvComp/indexd) deployments. It is built upon
a basic REST-like API and demonstrates how a client utility can be built to
interact with the index in a meaningful manner.

## Installation

The prototype implementation for the client is requests based. This
provides a minimum list of requirements and allows for deployment on a wide
range of systems with next to no configuration overhead. That said, it is
highly recommended to use pip and a virtualenv to isolate the installation.

To install the prototype implementation, simply run

```bash
pip install .
```

## Configuration

At present, all configuration options are hard-coded in the prototype. This
will be subject to change in the future, as options are moved to configuration
files. Until that time, the primary hard-coded configurations to keep in
mind is the index host and port combination.

```python
HOST = 'localhost'
PORT = 8080
```

## Index Records

Records are collections of information necessary to as-uniquely-as-possible
identify a piece of information. This is done through the use of hashes and
metadata. Records are assigned a UUIDv4 at the time of creation. This allows
records to be uniquely referenced amongst multiple records. To prevent an
update conflict when multiple systems are editing the same record, a revision
is stored and changed for every update. This is an opaque string and is
not used for anything other than avoiding update conflicts.

Hashes used by the index are deployment specific, but are intended to be the
results of widely known and commonly available hashing algorithms, such as
MD5 or SHA1. This is similar to the way that torrents are tracked, and provides
a mechanism by which data can be safely retrieved from potentially untrusted
sources in a secure manner.

Additional metadata that is store in index records include the size of the
data as well as the type.

Records adhere to the json-schema described in [indexd](https://github.com/LabAdvComp/indexd/blob/master/indexd/index/schema.py#L1):


An example of one such record:

```json
{
    "id": "119d292f-b786-421e-a8dd-72208e77c269",
    "rev": "dbee8496-5d03-4fbd-9115-6871c4ebf59f",
    "size": 512,
    "hash": {
        "md5": "e2a3a55aa1596f87f502c8ff29d74244",
        "sha1": "cb4e5ba5d30fd4667beba95bf73ea9d76ad3dcd4",
        "sha256": "20b599fa98f5f98e89e128ba6de3b65ff753c662721f368649fb8d7e7d4933b0"
    },
    "type": "object",
    "urls": [
      "s3://endpointurl/bucket/key"
    ]
}
```


## Making Queries


All queries to the index are made through HTTP using JSON data payloads.
This gives a simple means of interaction that is easily accessible to any
number of languages.

These queries are handled via requests and wrapped into the index client.


  ### Create a record ###


# Method: create

Required Arguments:
  hashes (dict): {hash type: hash value,}
      eg: ``hashes={'md5': ab167e49d25b488939b1ede42752458b'}``
  size (int): file size metadata associated with a given uuid

Optional Arguments:
  did (str): GUID (Global Unique Identifier) for the new indexd to be made
  urls (list): list of URLs where you can download the UUID
  acl (list): access control list
  authz (str): RBAC string
  file_name (str): name of the file associated with a given UUID
  metadata (dict): additional key value metadata for this entry
  urls_metadata (dict): metadata attached to each url
  baseid (str): optional baseid to group with previous entries versions
  version (str): entry version string

Return Value:
  Document: indexclient representation of an entry in indexd

Example: 

 indexclient.create(
    hashes = {'md5': ab167e49d25b488939b1ede42752458b'},
    size = 5,
    # optional arguments
    acl = ["a", "b"]
  )

  ### Retrieve a record ###


# Method: get

Required Argument:
  did (str): GUID (Global Unique Identifier) for the new indexd to be made

Return Value:
  Document: indexclient representation of an entry in indexd

Example:

 indexclient.get(did)  

# Method: global_get

Required Argument:
  did (str): GUID (Global Unique Identifier) for the new indexd to be made

Optional Argument:
  no_dist (Bool): Specify if you want a distributed search or not

Return Value:
  Document: indexclient representation of an entry in indexd

Example:

 indexclient.global_get(did)  
 or
 indexclient.global_get(did, no_dist=True)

# Method: get_with_params

Optional Argument:
  params (dict): a dictionary object containing some of the attributes of                   the desired record
      eg: ``{'hashes': {'md5': '...'}, 'size': '...', 'metadata': {'file_state': '...'}}``.
    - need to include all the hashes in the request 

Return Value:
  Document: indexclient representation of an entry in indexd

Example:

 params = {
   'hashes': {'md5': ab167e49d25b488939b1ede42752458b'}, 
   'size': 5
   # or any other params (metadata, acl, authz, etc.)
   }
 indexclient.get_with_params(params)


  ### Retrieve multiple records ###


# Method: bulk_request

Required Argument:
  dids (list): dids (list): list of dids for potential documents

Return Value:
  list: Document objects representing index records

Example:

 dids = [
   'did1',
   'did2',
   'did3',
   'did4'
 ]
 indexclient.bulk_request(dids)


  ### Update a record ###


First: get a Document object of the desired record with one of the get methods
Second: Update any of the records updatable attributes.
  - the format to do this is: ``doc.attr = value``
      - eg: ``doc.file_name = new_file_name``
  - Updatable attributes are: UPDATABLE_ATTRS = 
    [ "file_name",
      "urls",
      "version", 
      "metadata",
      "acl",
      "authz",
      "urls_metadata" ]

Lastly: Update all the local changes that were made to indexd using the 
        Document patch method: doc.patch()

Example:

 1. doc = indexclient.get('did') # or any other get method (global_get,
          etc.)
 2. doc.metadata["dummy_field"] = "dummy var"
    doc.acl = ['a', 'b']
    doc.version = '2'
 3. doc.patch()
`

  ### Delete a record ###


First: get a Document object of the desired record with one of the get methods
Second: Delete the record from indexd with the delete method: doc.delete()
Lastly: Check if the record was deleted with: if doc._deleted

Example: 

  1. doc = indexclient.get('did') # or any other get method (global_get,
           etc.)
  2. doc.delete()
  3. if doc._deleted == False:
        return "Record is not deleted"