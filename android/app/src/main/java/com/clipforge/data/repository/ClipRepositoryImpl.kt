package com.clipforge.data.repository

import com.clipforge.data.remote.api.ClipApi
import com.clipforge.domain.model.Clip
import com.clipforge.domain.repository.ClipRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject

class ClipRepositoryImpl @Inject constructor(
    private val api: ClipApi
) : ClipRepository {
    override fun getClips(): Flow<Result<List<Clip>>> = flow {
        try {
            emit(Result.success(api.getClips()))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
}
