package com.clipforge.domain.repository

interface JobRepository {
    suspend fun getJobs(): Result<List<Any>>
}
