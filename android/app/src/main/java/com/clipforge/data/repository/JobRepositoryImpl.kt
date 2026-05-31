package com.clipforge.data.repository

import com.clipforge.data.remote.api.JobApi
import com.clipforge.domain.repository.JobRepository
import javax.inject.Inject

class JobRepositoryImpl @Inject constructor(
    private val api: JobApi
) : JobRepository {
    override suspend fun getJobs(): Result<List<Any>> {
        return try {
            val response = api.getJobs()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
