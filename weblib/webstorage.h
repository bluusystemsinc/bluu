#ifndef WEBSTORAGE_H
#define WEBSTORAGE_H

#include <QObject>
#include <QVariantList>
#include <QVariantMap>
#include <QNetworkRequest>
#include <QPointer>
#include "items.h"
#include "webstorageresponse.h"

class QNetworkAccessManager;
class GameSessionData;

namespace GLOBAL {
    class Payment;
    class Guest;
}

/**
 * \defgroup WebStorage Web storage
 * @{
 * \brief Programmatic access to the web service
 *
 * The web storage module provides progammatic access to the web storage
 * in a thread-safe manner. Each response can be observed using the
 * returned WebStorageResponse.
 *
 * Here is an example of a hypothetical request object which fetches
 * an email associated with a hypothetical credit-card endpoint (which
 * only stores a hash of the primary account number, the name, and the
 * email, for hypothetical PCI compliance):
 *
 \code
 // emailcc.h
 class EmailForCCFetcher
 {
    Q_OBJECT
 public:
     EmailForCCFetcher(QString panHash);
 public slots:
     void onCcRetrieved(WebStorageResponse * response);
 signals:
     void emailRetrieved(QString);
 };


 // emailcc.cpp
 EmailForCCFetcher::EmailForCCFetcher(QString panHash)
 {
     QString urlSuffix = QString("cc/%1").arg(panHash);
     WebStorageResponse * response = gCore->storage()->get(urlSuffix);
     connect(response, SIGNAL(finished(WebStorageResponse *)),
             this, SLOT(onCcRetrieved(WebStorageResponse *)));
 }

 void EmailForCCFetcher::onCcRetrieved(WebStorageResponse * response)
 {
     QVariant ccData = response->jsonContent();
     response->deleteLater();

     if (!ccData.isValid()) {
         log_error("Could not parse data from CC endpoint!", "foo", "emailcc");
         return;
     }

     emit emailRetrieved(ccData.toMap().value("email").toString());
 }
 \endcode
 */

/*!
 * \brief A programmatic interface to the web service
 *
 * The WebStorage API is structured so that multiple clients can make requests
 * to a single WebStorage instance, which communicates with a webservice
 * specified by the Storage/hostname setting in app.ini. Responses to client
 * requests are represented as WebStorageResponse objects. Clients must connect
 * signals on each WebStorageResponse object instead of on the WebStorage
 * itself; this helps to prevent different clients from intercepting each
 * other's messages.
 */
class WebStorage : public QObject
{
    Q_OBJECT
public:

    explicit WebStorage(QObject *parent = 0);

    /*!
     * \brief Send a GET request to the web service
     *
     * \param urlSuffix the absolute path (ex. "waiter/dennys/77777") to fetch.
     */
    WebStorageResponse * get(QString urlSuffix);

    /*!
     * \brief Send a POST request to the web service
     *
     * \param urlSuffix the absolute path (ex. "waiter/dennys/77777") to fetch.
     * \param rawContent the raw bytestream to send.
     */
    WebStorageResponse * post(QString urlSuffix, QByteArray rawContent);

    /*!
     * \brief Send JSON data in a POST request to the web service
     *
     * \param urlSuffix the absolute path (ex. "waiter/dennys/77777") to fetch.
     * \param jsonContent a QVariant to be POSTed as JSON. The QVariant _must_
     *        be valid.
     */
    WebStorageResponse * postJson(QString urlSuffix, QVariant jsonContent);

    /*!
     * \brief Retrieve waiter details (ex. name, bio, photo, etc.)
     * \returns A pointer to the WebStorageResponse encapsulating the response
     *          details. The response will contain a QVariant list, which
     *          will contain either 0 or 1 entries, depending on whether any
     *          matching waiter was found.
     */
    WebStorageResponse * getWaiterInfo();

    /*!
     * \brief Get a list of top scores for a game
     *
     * \param gameName the case-sensitive canonical name of the
     *        game (ex. "Memory").
     * \param count the number of scores to retrieve.
     * \param descendingOrder true if the games with the highest scores should
     *        be fetched, or false if games with lower scores are preferred.
     * \param level the case-sensitive canonical name of the level
     *        (ex. "medium").
     *
     * \returns A pointer to the WebStorageResponse encapsulating the response
     *          details. The response will contain a QVariantList of the highest
     *          or lowest scores, depending on the value of descendingOrder.
     */
    WebStorageResponse * getGameTopScores(QString gameName, int count, bool descendingOrder, QString level = QString());

    /*!
     * \brief Get scores near to a specified score for a game
     *
     * \param gameName the case-sensitive canonical name of the
     *        game (ex. "Memory").
     * \param score
     * \param count the number of scores above and below the specified score
     *        to retrieve; for example, specifying a count of 2 would return
     *        the closest two scores above the specified score, and the closest
     *        two scores below the specified score.
     * \param level the case-sensitive canonical name of the level
     *        (ex. "medium").
     *
     * \returns A pointer to the WebStorageResponse encapsulating the response
     *          details. The response will consist of a QVariantMap containing
     *          two entries: "above" and "below", each of which contains a list
     *          of games with scores higher and lower than the queried score.
     */
    WebStorageResponse * getGameScores(QString gameName, int score, int count, QString level = QString());

    /*!
     * \brief Get the ranking (ex. 1st) for a game score
     *
     * \param gameName the case-sensitive canonical name of the
     *        game (ex. "Memory").
     * \param score the score for which the ranking should be computed.
     * \param descendingOrder true if the games with the highest scores should
     *        be fetched, or false if games with lower scores are preferred.
     * \param level the case-sensitive canonical name of the level
     *        (ex. "medium").
     *
     * \returns A pointer to the WebStorageResponse encapsulating the response
     *          details. The response will consist of an integer as a QVariant
     *          ranking the specified score, starting from 1 (the best ranking.)
     */
    WebStorageResponse * getGameScoreRanking(QString gameName, int score, bool descendingOrder, QString level = QString());

    /*!
     * \brief Save a guest's data to the webservice
     * \returns a pointer to a WebStorageResponse. If the response will be
     *          unused, it can be ignored and will delete itself after
     *          the request completes.
     */
    WebStorageResponse * saveGuest(GLOBAL::Guest * guest);

    /*!
     * \brief Save a payment to the webservice
     *
     * Save a payment to the webservice. Payment data includes summary
     * order data (ex. the subtotal, total, tip, and tax), the items
     * paid for (which may be a subset of the order items in the case
     * of a split bill), identifiers for the session (ex. the device,
     * table, server, etc.) and feedback.
     *
     * This method is also indirectly responsible for sending receipts
     * to customers: if the receipt type is "email", an email will be
     * sent to the address provided.
     *
     * \returns a pointer to a WebStorageResponse. If the response will be
     *          unused, it can be ignored and will delete itself after
     *          the request completes.
     */
    WebStorageResponse * savePayment(GLOBAL::Payment * payment);

    /*!
     * \brief Save an order to the webservice
     * \returns a pointer to a WebStorageResponse. If the response will be
     *          unused, it can be ignored and will delete itself after
     *          the request completes.
     */
    WebStorageResponse * saveOrder(ITEMS::BILL_ITEM_LIST sentItems);

    /*!
     * \brief Save a game to the webservice
     * \returns a pointer to a WebStorageResponse. If the response will be
     *          unused, it can be ignored and will delete itself after
     *          the request completes.
     */
    WebStorageResponse * saveGameSession(GameSessionData * session);

    /*!
     * \brief Update the current device's information on the webservice
     *
     * This function updates the device registry with the current values
     * of the restaurant code, IP address, software revision, table, and
     * waiter based on the device's MAC address.
     */
    WebStorageResponse * saveDeviceInfo();

private:
    QNetworkRequest createRequest(QString urlSuffix);

private:
    QNetworkAccessManager * m_manager;
    QString m_hostName;
};

/**
 * @}
 */

#endif // WEBSTORAGE_H
