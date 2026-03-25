



Create a proper workflow for agents to work . Along with proper documentation based on user information below:

00:00
Let me summarize the complete workflow for release management. The key is that a release happens for a resting date. During the release process, a user may ask for. Give me the next. Resting date for that wasting date. To be inquired. There will be an API that will be called for getting the next resting dates.

00:28
Now, this API made is sent. A set of different values for the dates. But when set the next wasting date. The agent will figure out the next Westing, which will be greater than equal to today's date. The Next Step would be. Getting the details of the Westing for which another API will be called under the name.

00:53
Get twisting details for that date. What this will do? It is going to create a token. Which will be placed into an S3 bucket. This token is. Equal to a Json file. This Json file is read by the tool and converted into a data frame. Questions can be asked on this data frame using the data analysis tool.

01:27
After wasting details have been calculated, the next step in the release process would be. Either to simulate a release or? To final, take it for approval. Both the steps would require tax calculation to happen. Tax calculation means various values from the users. Values like? Fnb. Sales price, depending on the tax.

01:58
Type. For some tax types, sales price is not required. Then performance. Numbers for the final tax calculation to happen. Depending on what uses have provided, the API will be called. For tax execution. Once the tax execution has happened. The token file that we created at the time of listing details gets updated with the new values for the columns, like FMV sales breaks tax.

02:41
Now, the data is ready to be analyzed after tax calculation. The next step in the workflow would be creating a URL for either reviewing the simulation or approving. For the release. This is where release process would end. While in the process of creating a release, a user has an option to filter on different parameters and create small batch sizes for both simulation or approval, the batch could be filtered based on, say, officer, non-officer, different region types, different types of tax liabilities, different types of Grant types.

03:26
The moment the user asks about a different? Type of filtration say, I want to simulate a release for rsus. Means that we will go through the process of. Seeing that, okay, what is the date? What is the wasting information from that listing information pull in only the RSU component and then?

03:50
Go for the tax calculation by asking the required parameters for simulation. Approval. This is the overall flow for the tax.
