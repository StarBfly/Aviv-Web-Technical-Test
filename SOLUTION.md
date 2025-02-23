# AVIV technical test solution

You can use this file to write down your assumptions and list the missing features or technical revamp that should
be achieved with your implementation.

## Notes

Before implementing the listings price history endpoint, I first need to determine an effective way to store the history of price changes. Currently, this isn't possible, as updates overwrite existing data in the listings table based on the ID.
To preserve a record of price changes, I have considered four possible solutions:

|                                                              | 🌸 pros                                                       | 💀cons                                                        |
|--------------------------------------------------------------|--------------------------------------------------------------|--------------------------------------------------------------|
| Slowly Changing Dimensions<br> (SCD) Type 4<br>(Store all the historical data <br>In the separate table<br> to track changes) | - easy and fast<br> to implement <br>for relational DBs<br>- works well with SQL<br> indexes | - the data amount could become very massive in the future (more storage required, performance issues)<br>- could get complicated to track data that is changed too quickly<br>- needs migration if new column changes needs to be tracked in the future<br> |
| Event Sourcing pattern<br>(store every change as an event rather than updating or inserting rows, like event: PRICE UPDATE/PHONE UPDATE etc.) | - great to inspect overall changes and for rollback<br>- flexible (since different events can be stored in a single history table)<br>- nice for an overall event driven solutions (like Kafka)<br> | - hard to query<br>- the data storage will be enormous since it track every update event<br>- not suitable for relational DBs and best for NoSQL |
| Temporal Tables (as an SQL Feature)<br>(A built-in SQL feature where the database automatically tracks history without needing to manually insert new rows.) | - the history could be handled automatically <br>- easy to query<br>- works sort of “out of box” | - slightly overheaded than a standard table<br>- not so easily available for all DBs (for example for Postgres, that is used in current API, the temporal table and all the triggers need to be implemented manually. So it’s a bit overengineering |
| Another separate DB of different kind to store the history (NoSQL or data warehouse like Redshift or BigQuery) | - fast read/write<br>- easy scalability<br>- in case of data warehouse like Redshift or BigQuery even the statistics, data aggregations and trends could be available  | - data update synchronisation could be tricky<br>- hard and expensive (defiantly a overkill for current task) |

Taking into account the pros and cons, I have decided that the best approach for the current small API and relatively small dataset in the PostgreSQL database is **Slowly Changing Dimensions Type 4**, utilizing a separate table for tracking price history.

## Decisions and Key Considerations in the New SQL Script for History Storage
While designing the SQL script for creating a new database table to store price history, I made the following:
### 1. Establishing Relationships
To ensure data integrity, I added a **foreign key constraint** linking the listing_price_history table to the listings table. This maintains a clear relationship between listings and their historical price records:

Also I've added ON DELETE CASCADE to ensure that when a listing is deleted, its associated price history is also removed
This prevents orphaned records and keeps the database clean.

### 2. Optimizing Query Performance with Indexing
Since the price history table might grow over time, I've added an **index on** listing_id to improve query performance when retrieving historical price data:

### 3. Repopulating the Table
To ensure a smooth transition, I considered repopulating the newly created history table with existing data.

## Simplifying the Code – Removing Unnecessary Mappers
I believe that the **mappers module** was not really necessary, as it contained only two static methods. To simplify the architecture, I removed it.
Instead I've added:
* The to_dict **method** is relevant to the model itself and should be stored within it.
* The **dict** that makes the conversion from entity to Pydantic model belongs within the respective Pydantic model module.

## Changing the **update** logic

I also modified the update method in the ListingRepository. Previously, it operated by deleting the existing row and inserting a new one. However, this approach disrupted the relationship between listings and their price history.

Since the rationale behind using delete-and-insert was unclear, I opted for a more straightforward and reliable solution—replacing it with a standard SQLAlchemy update statement. This ensures data integrity while preserving the link between listings and their historical price records.

## Questions

This section contains additional questions your expected to answer before the debrief interview.

- **What is missing with your implementation to go to production?**

- **How would you deploy your implementation?**

- **If you had to implement the same application from scratch, what would you do differently?**

- **The application aims at storing hundreds of thousands listings and millions of prices, and be accessed by millions
  of users every month. What should be anticipated and done to handle it?**

  NB: You must update the [given architecture schema](./schemas/Aviv_Technical_Test_Architecture.drawio) by importing it
  on [diagrams.net](https://app.diagrams.net/) 
