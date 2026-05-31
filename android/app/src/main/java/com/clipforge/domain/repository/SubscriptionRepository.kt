package com.clipforge.domain.repository

import kotlinx.coroutines.flow.Flow

interface SubscriptionRepository {
    fun getSubscription(): Flow<Result<Any>>
}
