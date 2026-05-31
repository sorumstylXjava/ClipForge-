package com.clipforge.data.repository

import com.clipforge.data.remote.api.SubscriptionApi
import com.clipforge.domain.repository.SubscriptionRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject

class SubscriptionRepositoryImpl @Inject constructor(
    private val api: SubscriptionApi
) : SubscriptionRepository {
    override fun getSubscription(): Flow<Result<Any>> = flow {
        try {
            emit(Result.success(api.getSubscription()))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
}
