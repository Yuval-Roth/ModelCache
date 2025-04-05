package utils

import java.io.IOException
import java.net.URI
import java.net.URLEncoder
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.nio.charset.StandardCharsets
import java.util.*

class RestApiClient {
    private var uri: String? = null
    private val headers: MutableMap<String, String> = HashMap()
    private val params: MutableMap<String, String> = HashMap()
    private var body: String = ""
    private var isPost = false

    /**
     * @throws IOException if there is an error sending the request
     * @throws InterruptedException if the operation is interrupted
     * @throws IllegalStateException if the URI is not set or there are any issues with the request
     */
    fun send(): String {

        val uri = this.uri ?: throw IllegalStateException("URI is required")

        // build full URI
        val fullUri = params.entries.fold(uri) { acc, entry ->
            val separator = if (acc.contains("?")) "&" else "?"
            val encodedKey = URLEncoder.encode(entry.key, StandardCharsets.UTF_8.toString())
            val encodedValue = URLEncoder.encode(entry.value, StandardCharsets.UTF_8.toString())
            "$acc$separator$encodedKey=$encodedValue"
        }

        // build request
        val request = HttpRequest.newBuilder()
            .uri(URI.create(fullUri))
            .apply{
                if(! headers.containsKey("Content-Type")) {
                    header("Content-Type", "application/json")
                }
                if (isPost) POST(HttpRequest.BodyPublishers.ofString(body))
                headers.forEach { (name, value) -> header(name, value) }
            }.build()

        // send request
        val client = HttpClient.newHttpClient()
        val response = client.send(request, HttpResponse.BodyHandlers.ofString())
        return response.body()
    }

    /**
     * Set the body of the request. Must be used with [withPost] to have
     * any effect
     */
    fun withBody(body: String) = apply {
        this.body = body
    }

    /**
     * Set the request method to POST. If [withBody] is not called,
     * the body will be empty
     */
    fun withPost() = apply {
        isPost = true
    }

    /**
     * Set the URI of the request.
     *
     * Must not be blank and must not contain
     * query parameters ('?', '&', '=') or spaces.
     *
     * @throws IllegalStateException if there are any issues with the URI
     */
    fun withUri(uri: String) = apply {
        assert(uri.isNotBlank()) { "URI should not be blank" }
        assert(!uri.contains("?")) { "URI should not contain query parameters" }
        assert(!uri.contains("&")) { "URI should not contain query parameters" }
        assert(!uri.contains("=")) { "URI should not contain query parameters" }
        assert(!uri.contains(" ")) { "URI should not contain spaces" }

        this.uri = uri
    }

    /**
     * Set a header for the request.
     * @throws IllegalStateException if the header is already set
     */
    fun withHeader(key: String, value: String) = apply {
        assert(!headers.containsKey(key)) { "Header %s set more than once".format(key) }
        headers[key] = value
    }

    /**
     * Set a parameter for the request.
     * @throws IllegalStateException if the parameter is already set
     */
    fun withParam(key: String, value: String) = apply {
        assert(!params.containsKey(key)) { "Param %s set more than once".format(key) }
        params[key] = value.replace(" ".toRegex(), "%20") // replace spaces with %20
    }

    /**
     * Set multiple parameters for the request.
     * @param params a map of parameters to set
     * @throws IllegalStateException if any parameter is already set
     */
    fun withParams(params: Map<String, String>) = apply {
        params.forEach { (key: String, value: String) -> this.withParam(key, value) }
    }

    /**
     * Set multiple parameters for the request.
     * @param params a vararg of pairs of parameters to set
     * @throws IllegalStateException if any parameter is already set
     */
    @SafeVarargs
    fun withParams(vararg params: Pair<String, String>) = apply {
        Arrays.stream(params).forEach { p: Pair<String, String> -> this.withParam(p.first, p.second) }
    }
}
