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

### Minor Code Refactoring
* I would create a separate package for models, with each model stored in its own module. This will enhance maintainability, readability, and scalability in future iterations.
Since every entity already has its own module, it makes sense to store the corresponding models in separate modules as well.
* Additionally, introducing a Factory pattern for use cases could be beneficial. This would help make the architecture more modular and layered, improving flexibility for future enhancements.

### Add exception handling
The application needs better user-friendly Error handling.

### Unit Tests and CI
I would expand unit tests to increase test coverage and ensure more robust validation of business logic and add the intergration tests with the CI to run all the QC.

### Database Maintenance
Integrating the Alembic migration tool would simplify version upgrades and downgrades, making database schema management easier and more maintainable.

### API UI & Documentation
Adding Swagger would significantly improve user experience and documentation, making it easier to explore and interact with the API.

- **How would you deploy your implementation?**

For deployment, I would likely opt for a basic VPS approach, as the project is still in its early stages. The primary goal at this point is to ensure a fast and cost-efficient solution. Given these requirements, I believe AWS EC2 combined with PostgreSQL on RDS would be a suitable choice.

For a serverless architecture, I would consider AWS Fargate with Amazon RDS. While AWS Lambda is generally more cost-effective than Fargate, it may not be the best fit for this use case due to cold start latency, which could impact performance.

- **If you had to implement the same application from scratch, what would you do differently?**

If I were to build this application from scratch, I would likely choose **FastAPI** over Flask due. Here’s why:

**1. Performance**
FastAPI is significantly **faster** than Flask, thanks to its asynchronous capabilities and efficient request handling.

**2. Built-in Async Database Support**
FastAPI **natively supports async SQLAlchemy**. In contrast, Flask requires **additional setup** for async operations. Native async support improves scalability and responsiveness, especially for high-concurrency applications.

**3. Seamless Data Validation**
FastAPI works **beautifully with Pydantic** out of the box, providing **automatic request validation** for query parameters and body payloads. Flask, on the other hand, requires additional setup and custom validation logic.

**4. Automatic Interactive API Documentation**
FastAPI includes **Swagger UI** default, eliminating the need for third-party tools like Flask-Swagger. **Schemas and documentation are auto-generated**, saving time and effort while ensuring up-to-date API documentation.

**5. Dependency Injection for Cleaner Code**
FastAPI's **dependency injection system** simplifies code maintenance by managing database connections (and authentication logic, if it will be needed in the future) and makes it clean.

**6. A Fast-Growing, Modern Framework**
FastAPI is a **modern, rapidly evolving** framework with an active and growing community. And it has many regular improvements and updates .


- **The application aims at storing hundreds of thousands listings and millions of prices, and be accessed by millions
  of users every month. What should be anticipated and done to handle it?**


For future scalability, incorporating a NoSQL database to store historical data could be a valuable enhancement, for better performance. Alternatively, storing the history data in a data warehouse like BigQuery or Redshift would enable efficient SQL-based querying while also providing historical data analysis and trend investigation (for example to track price changes pver time).

To optimize performance, history updates could be handled asynchronously as a background job, ensuring that listing creation and updates remain fast and responsive. These background tasks could be executed using Amazon Batch or managed through a custom ETL pipeline, streamlining data processing without impacting the core application’s performance.


I've changed the schema a bit, but I believe the changes in backend do not effect this schema in any significant way. 

  NB: You must update the [given architecture schema](./schemas/Aviv_Technical_Test_Architecture.drawio) by importing it
  on [diagrams.net](https://app.diagrams.net/) 
