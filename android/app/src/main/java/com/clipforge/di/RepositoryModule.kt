package com.clipforge.di

import com.clipforge.data.repository.AuthRepositoryImpl
import com.clipforge.domain.repository.AuthRepository
import com.clipforge.data.repository.VideoRepositoryImpl
import com.clipforge.domain.repository.VideoRepository
import com.clipforge.data.repository.ClipRepositoryImpl
import com.clipforge.domain.repository.ClipRepository
import com.clipforge.data.repository.SubscriptionRepositoryImpl
import com.clipforge.domain.repository.SubscriptionRepository
import com.clipforge.data.repository.JobRepositoryImpl
import com.clipforge.domain.repository.JobRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    abstract fun bindAuthRepository(
        impl: AuthRepositoryImpl
    ): AuthRepository

    @Binds
    abstract fun bindVideoRepository(
        impl: VideoRepositoryImpl
    ): VideoRepository

    @Binds
    abstract fun bindClipRepository(
        impl: ClipRepositoryImpl
    ): ClipRepository

    @Binds
    abstract fun bindSubscriptionRepository(
        impl: SubscriptionRepositoryImpl
    ): SubscriptionRepository

    @Binds
    abstract fun bindJobRepository(
        impl: JobRepositoryImpl
    ): JobRepository
}
