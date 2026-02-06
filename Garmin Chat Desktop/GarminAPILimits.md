# Garmin API Limits and Data Access

## Overview

The Garmin Connect API (via the `garminconnect` library) has both **technical limits** and **practical considerations** when querying fitness data.

---

## Activity Query Limits

### **Per-Request Limits**

**Activities API (`get_activities`)**:
- **Technical limit**: ~100 activities per request (soft limit, not strictly enforced)
- **Recommended**: 20-50 activities per request for best performance
- **Default in app**: 5 activities (changed to configurable in v3.0+)

**Pagination Support**:
```python
# Get activities 0-49 (most recent 50)
activities = garmin_handler.get_activities(limit=50, start=0)

# Get activities 50-99 (next 50 older activities)
activities = garmin_handler.get_activities(limit=50, start=50)

# Get activities 100-149 (and so on...)
activities = garmin_handler.get_activities(limit=50, start=100)
```

### **Historical Data Access**

**Time Range**:
- Can access activities going back **as far as data exists** in your Garmin account
- No hard date limit (some users have data going back 10+ years)
- Limited only by:
  - Account age
  - Data retention in Garmin's system
  - API rate limits

**Total Activity Count**:
- **Practical limit**: ~500 activities in a single query session (app safety limit)
- **Actual limit**: Can fetch thousands via pagination, but not recommended
- **Recommended**: Query specific date ranges instead of fetching all activities

---

## Date-Specific Data Limits

### **Summary Data (`get_user_summary`)**
- **Scope**: Single day only
- **Date range**: Can query any date with data
- **Parameters**: Requires specific date (YYYY-MM-DD)

### **Sleep Data (`get_sleep_data`)**
- **Scope**: Single night/day
- **Date range**: Can query historical sleep data
- **Limitation**: One date at a time

### **Steps Data (`get_steps_data`)**
- **Scope**: Single day
- **Date range**: Any date with recorded data
- **Limitation**: One date per request

### **Heart Rate Data (`get_heart_rates`)**
- **Scope**: Single day
- **Date range**: Any date with data
- **Limitation**: Detailed minute-by-minute data may be large

---

## Rate Limits

### **Garmin's Unofficial Limits**

Garmin doesn't officially publish rate limits, but observed behavior:

**Requests per Minute**:
- **Soft limit**: ~20-30 requests/minute
- **Hard limit**: ~60 requests/minute
- **Exceeded result**: HTTP 429 (Too Many Requests)

**Requests per Hour**:
- **Estimated**: ~500-1000 requests/hour
- **Varies** by account and API endpoint

**Requests per Day**:
- **Practical limit**: ~5,000-10,000 requests/day
- **Most users never hit this**

### **Rate Limit Errors**

**HTTP 429 Response**:
```
Garmin has temporarily blocked your IP due to too many requests
```

**Solutions**:
1. Wait 15-30 minutes before retrying
2. Reduce request frequency
3. Implement exponential backoff
4. Cache data locally

**Prevention**:
- Don't repeatedly click "Refresh Data" button
- Avoid automated polling
- Use the app's built-in caching
- Query specific date ranges instead of all data

---

## Token Expiration

### **OAuth Token Lifetimes**

**Access Token**:
- **Lifetime**: 1 hour
- **Refresh**: Automatic via refresh token
- **Expiration result**: 401 Unauthorized

**Refresh Token**:
- **Lifetime**: ~30 days
- **Refresh**: Requires MFA re-authentication
- **Expiration result**: Must re-authenticate with MFA

### **Session Management**

The app handles token refresh automatically:
1. Access token expires → auto-refresh via refresh token
2. Refresh token expires → prompt for MFA
3. MFA successful → new tokens saved for 30 days

---

## Data Availability Limits

### **Real-Time Data**

**Sync Delay**:
- Data syncs from watch to Garmin Connect
- **Typical delay**: 5-15 minutes after sync
- **Factors**: Bluetooth/WiFi connection, watch model

**Data Types**:
- **Steps, heart rate**: Real-time (updates as watch syncs)
- **Activities**: Available immediately after saving on watch
- **Sleep**: Available after wake-up and sync
- **Body composition**: Manual entry or smart scale sync

### **Historical Data Retention**

**Garmin's Data Retention**:
- **Activities**: Indefinite (as long as account exists)
- **Daily summaries**: Indefinite
- **Detailed metrics**: Varies by data type
- **Minute-by-minute data**: May be aggregated after 90 days

---

## App-Specific Limits (Garmin Chat Desktop)

### **Current Implementation**

**Default Activity Fetch**:
- **Query detection**: 5 activities for most queries
- **Configurable**: Can be increased up to 100
- **Context limit**: AI models have token limits (~8K-128K tokens)

**Context Window Considerations**:
- **5 activities**: ~500 tokens
- **20 activities**: ~2,000 tokens
- **100 activities**: ~10,000 tokens
- **Recommendation**: Keep under 20 activities per query

### **New Features (v3.0+)**

**Configurable Activity Limits**:
```python
# In garmin_handler.py
def format_data_for_context(self, data_type: str = "summary", activity_limit: int = 5)
```

Users can modify this for queries requiring more history.

**Date Range Queries**:
```python
# New method added in v3.0
def get_activities_by_date(self, start_date: str, end_date: str)
```

Fetches activities within specific date range with automatic pagination.

---

## Best Practices

### **For Daily Use**

1. **Query Recent Data**: Default 5 activities is sufficient for most questions
2. **Use Date Ranges**: For historical analysis, specify date ranges
3. **Cache Results**: Save important queries to chat history
4. **Avoid Spam**: Don't repeatedly refresh if data hasn't changed

### **For Historical Analysis**

1. **Batch Requests**: Query by week/month instead of all-time
2. **Export Data**: Use export feature for long-term analysis
3. **Pagination**: For >100 activities, use multiple requests
4. **Rate Limiting**: Add delays between large batch requests

### **For Developers**

1. **Implement Caching**: Store frequently accessed data locally
2. **Exponential Backoff**: Retry failed requests with increasing delays
3. **Error Handling**: Catch 429 errors and wait before retry
4. **Batch Processing**: Group related queries together

---

## Query Examples

### **Recent Activities (Default)**
```python
# Fetch last 5 activities (default)
activities = garmin_handler.get_activities(limit=5)
```
**Use case**: "What was my last workout?"

### **More Activities**
```python
# Fetch last 20 activities
activities = garmin_handler.get_activities(limit=20)
```
**Use case**: "Show me my workouts this month"

### **Date Range Query**
```python
# Fetch activities from Jan 1-31, 2025
activities = garmin_handler.get_activities_by_date("2025-01-01", "2025-01-31")
```
**Use case**: "Compare my running in January vs February"

### **Paginated Query**
```python
# Fetch activities 50-99 (skip first 50)
activities = garmin_handler.get_activities(limit=50, start=50)
```
**Use case**: "Show me activities from 2 months ago"

---

## Technical Limitations Summary

| Item | Limit | Notes |
|------|-------|-------|
| **Activities per request** | ~100 | Soft limit, can vary |
| **Historical access** | Unlimited | As far back as data exists |
| **Requests per minute** | ~20-30 | Unofficial, observed |
| **Requests per hour** | ~500-1000 | Estimated |
| **Token lifetime (access)** | 1 hour | Auto-refreshed |
| **Token lifetime (refresh)** | ~30 days | Requires MFA after expiry |
| **Daily data queries** | Single date | One date per request |
| **Context window (AI)** | ~8K-128K tokens | Varies by model |
| **Recommended activities** | 5-20 | Balance detail vs tokens |

---

## Future Enhancements

### **Planned Features**

1. **Smart Pagination**: Automatically fetch more activities for date-range queries
2. **Caching Layer**: Local cache to reduce API calls
3. **Batch Query Optimizer**: Intelligently group related queries
4. **Rate Limit Detector**: Auto-detect and wait on 429 errors
5. **Historical Analysis**: Dedicated mode for multi-month queries

### **User-Requested Features**

- Monthly/yearly activity summaries
- Trend analysis over long periods
- Activity comparisons across seasons
- Performance progression tracking

---

## Troubleshooting

### **"Not Enough Activities Returned"**

**Cause**: Query is limited to 5 activities by default

**Solution**: 
1. Modify `format_data_for_context()` to increase `activity_limit`
2. Or use direct API calls with higher limits

### **"Rate Limit Exceeded (429)"**

**Cause**: Too many API requests in short time

**Solution**:
1. Wait 15-30 minutes
2. Reduce request frequency
3. Don't spam "Refresh Data" button

### **"No Data for This Date"**

**Cause**: Either no activity on that date or date format incorrect

**Solution**:
1. Verify date format (YYYY-MM-DD)
2. Check if watch synced data for that date
3. Try adjacent dates

### **"Token Expired"**

**Cause**: Refresh token expired (>30 days)

**Solution**:
1. Click "Connect to Garmin"
2. Enter MFA code when prompted
3. Tokens saved for next 30 days

---

## Conclusion

The Garmin API is quite generous with limits for personal use:
- ✅ **Historical data**: Access goes back years
- ✅ **Pagination**: Fetch hundreds of activities if needed
- ✅ **Rate limits**: Reasonable for normal usage
- ⚠️ **Per-request**: Limited to ~100 activities
- ⚠️ **Tokens**: Refresh every 30 days with MFA

For 99% of use cases, the default limits are more than sufficient. Power users can easily extend the app to fetch more data as needed.