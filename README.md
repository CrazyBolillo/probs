# Probs
Calculate the probability of your internet dying.

Probably not as cool as it sounds. This is a homework assignment which calculates
the average bandwidth and chances of your internet completely dying, based on how
many providers you have.

It takes into the account the provider's uptime and speed in megabits.

## Usage
```
usage: probs.py [-h] file output

positional arguments:
  file        File containing ISPs' information
  output      Path where output will be written to

options:
  -h, --help  show this help message and exit

```

## Example
This is an example configuration file:
```
{
  "providers": [
    {
      "name": "Telmex",
      "uptime": 95,
      "megabits": 50
    },
    {
      "name": "Megacable",
      "uptime": 90,
      "megabits": 60
    }
  ]
}
```
