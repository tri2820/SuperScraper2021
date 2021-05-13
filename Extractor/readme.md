# Data Extractor
## Summary
Calling the `extract()` function will pull all super performance from the database and output `performance.csv` and `performance_pivot.csv` in an easily readible and manipulated file

## More Detail
### Inclusion
To include the extractor in another piece of code, it needs to be Included. An example of this, from the SuperScraper root directory would be `from Extractor.extractor import extract` and then in the code where you want to call the function, simply have `extract()`

### Outputs
Seeing as a table can be output in two different ways, with the X and Y axis flipped, both of these are output here. The period is typically on a month by month basis, in the format YYYY-MM
#### **Performance.csv**
As you can see this has the period along the x axis, funds along the y
...  | period_1 | period_2 | period_3 | ... | period_n 
-----|-----|-----|-----|-----|-----|
 fund_1 | performance | performance | performance | ... | performance 
 fund_2 | performance | performance | performance | ... | performance 
 fund_3 | performance | performance | performance | ... | performance 
 ... | ... | ... | ... | ... | ... 
 fund_n | performance | performance | performance | ... | performance 

#### **Performance_pivot.csv**
This is the transposed table, with funds along the x axis and periods down the y
|...  | fund_1 | fund_2 | fund_3 | ... | fund_n |
|------|------|------|------|------|------|
| period_1 | performance | performance | performance | ... | performance |
| period_2 | performance | performance | performance | ... | performance |
| period_3 | performance | performance | performance | ... | performance |
| ... | ... | ... | ... | ... | ... |
| period_n | performance | performance | performance | ... | performance |


