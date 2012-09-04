#include "webstorage.h"
#include "globals.h"
#include "core.h"
#include "webstorageresponse.h"
#include "items.h"
#include "game_interface.h"
#include <QJson/Serializer>


#define USER ""
#define PASSWORD ""


WebStorage::WebStorage(QObject *parent) :
    QObject(parent)
{
    m_manager = new QNetworkAccessManager(this);
    m_hostName = gCore->settingValue("Storage/hostName", "https://*******.com").toString();
}


QNetworkRequest WebStorage::createRequest(QString urlSuffix)
{
    QString url(QString("%1/%2").arg(m_hostName).arg(urlSuffix));
    QString authorization = QString("%1:%2").arg(USER).arg(PASSWORD);
    QNetworkRequest request;

    request.setUrl(url);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    request.setRawHeader("Authorization", "Basic " + QByteArray(authorization.toAscii()).toBase64());

    return request;
}


WebStorageResponse * WebStorage::get(QString urlSuffix)
{
    QNetworkRequest request = createRequest(urlSuffix);
    QString message = QString("Fetching data from %1")
           .arg(request.url().toString());
    log_debug(message, "webstorage");

    QNetworkReply * reply = m_manager->get(request);
    return new WebStorageResponse(reply);
}


WebStorageResponse * WebStorage::post(QString urlSuffix, QByteArray rawContent)
{
    QNetworkRequest request = createRequest(urlSuffix);
    QString message = QString("Sending request to %1\n%2\n")
            .arg(request.url().toString())
            .arg(QString(rawContent));
    log_debug(message, "webstorage");

    QNetworkReply * reply = m_manager->post(request, rawContent);
    return new WebStorageResponse(reply);
}


WebStorageResponse * WebStorage::postJson(QString urlSuffix, QVariant jsonContent)
{
    Q_ASSERT(jsonContent.isValid());
    QJson::Serializer serializer;
    return post(urlSuffix, serializer.serialize(jsonContent));
}


QString getRestaurantCode()
{
    return gCore->settingValue("RestaurantId").toString();
}


QString getCheckNumber()
{
    return gCore->settingValue("CheckNum/Value").toString();
}


QString getTableNumber()
{
    return gCore->settingValue("TableNum/Value").toString();
}


QString getServerNumber()
{
    return gCore->settingValue("ServerNum/Value").toString();
}


QString getTimeZoneOffset()
{
    QDateTime localTime = QDateTime::currentDateTime();
    QDateTime utcTime = localTime.toUTC();
    localTime.setTimeSpec(Qt::UTC);

    int offset = utcTime.secsTo(localTime);
    int offsetMinutes = abs(offset) / 60 % 60;
    int offsetHours = abs(offset) / 3600;

    QString sign = QString(offset > 0 ? "+" : "-");

    return QString("%1%2%3")
        .arg(sign)
        .arg(offsetHours, 2, 10, QLatin1Char('0'))
        .arg(offsetMinutes, 2, 10, QLatin1Char('0'));
}


WebStorageResponse * WebStorage::getWaiterInfo()
{
    // URL Pattern: /waiter/<restaurant_code>/<waiter_pos_id>/
    QString urlSuffix = QString("waiter/%1/%2/?format=json")
            .arg(getRestaurantCode())
            .arg(getServerNumber());

    return get(urlSuffix);
}


WebStorageResponse * WebStorage::getGameTopScores(QString gameName, int count, bool descendingOrder, QString level)
{
    // URL Pattern: /scores/top/<game_name>/<restaurant_code>/<count>/[level]
    QString order = descendingOrder ? "top": "minimum";

    QString urlSuffix = QString("scores/"+order+"/%1/%2/%3/%4")
            .arg(gameName)
            .arg(getRestaurantCode())
            .arg(count)
            .arg(level.isEmpty() ? "" : level + "/");

    return get(urlSuffix);
}


WebStorageResponse * WebStorage::getGameScores(QString gameName, int score, int count, QString level)
{
    // URL Pattern: /scores/nearest/<game_name>/<restaurant_code>/<score>/<count>/[level]
    QString urlSuffix = QString("scores/nearest/%1/%2/%3/%4/%5")
            .arg(gameName)
            .arg(getRestaurantCode())
            .arg(score)
            .arg(count)
            .arg(level.isEmpty() ? "" : level + "/");

    return get(urlSuffix);
}


WebStorageResponse * WebStorage::getGameScoreRanking(QString gameName, int score, bool descendingOrder, QString level)
{
    // URL Pattern: /scores/ranking/<game_name>/<restaurant_code>/<score>/[level]

    QString order = descendingOrder? "ranking":"descending-ranking";

    QString urlSuffix = QString("scores/"+order+"/%1/%2/%3/%4")
            .arg(gameName)
            .arg(getRestaurantCode())
            .arg(score)
            .arg(level.isEmpty() ? "" : level + "/");

    return get(urlSuffix);
}


WebStorageResponse * WebStorage::saveGuest(GLOBAL::Guest * guest)
{
    QString urlSuffix = QString("email/");
    QVariantMap p;

    p.insert("restaurant_code", getRestaurantCode());
    p.insert("pos_check_number", getCheckNumber());
    p.insert("table_number", getTableNumber());
    p.insert("waiter_code", getServerNumber());
    p.insert("device_mac", gCore->deviceID());
    p.insert("email", guest->email);
    p.insert("joined_club", guest->joined_club);

    return postJson(urlSuffix, p);
}


WebStorageResponse * WebStorage::savePayment(GLOBAL::Payment * payment)
{
    QString urlSuffix = QString("payment/");
    QVariantMap p;
    QDateTime now = QDateTime::currentDateTime();
    QString dateTimeString = QString("%1%2")
        .arg(now.toString("yyyy-MM-dd'T'hh:mm:ss"))
        .arg(getTimeZoneOffset());

    p.insert("restaurant_code", getRestaurantCode());
    p.insert("pos_check_number", getCheckNumber());
    p.insert("table_number", getTableNumber());
    p.insert("waiter_code", getServerNumber());
    p.insert("device_mac", gCore->deviceID());
    p.insert("tender_type",payment->pay_method);
    p.insert("survey_stars", payment->star_rating);
    p.insert("turn_time", payment->turn_time);
    p.insert("receipt", payment->receipt);
    p.insert("experience", payment->experience);
    p.insert("split_type", payment->splitType);
    p.insert("signature", payment->signature.toBase64());
    p.insert("email", payment->email);
    p.insert("joined_club", payment->joined_club);
    p.insert("timestamp", dateTimeString);

    QVariantList items;
    foreach (ITEMS::BILL_ITEM item,  payment->items) {
        QVariantMap menu_item;
        QVariantList modifiers;
        menu_item.insert("item_number", item.menuID);
        menu_item.insert("item_price", item.price);
        menu_item.insert("item_name", item.itemname);
        menu_item.insert("quantity", item.quantity);

        foreach (ITEMS::ModifierRepItem option, item.options) {
            QVariantMap modifier;
            modifier.insert("item_number", option.itemno);
            modifier.insert("item_price", option.price);
            modifier.insert("item_name",  option.itemname);

            modifiers.append(modifier);
        }

        menu_item.insert("modifiers", modifiers);
        items.append(menu_item);
    }

    p.insert("items", items);
    p.insert("subtotal", payment->subtotal);
    p.insert("tax", payment->tax);
    p.insert("total", payment->total);
    p.insert("tip", payment->tip);

    return postJson(urlSuffix, p);
}


WebStorageResponse * WebStorage::saveOrder(ITEMS::BILL_ITEM_LIST sentItems)
{
    QString urlSuffix = QString("order/");
    QVariantMap order;
    order.insert("restaurant_code", getRestaurantCode());
    order.insert("pos_check_number", getCheckNumber());
    order.insert("device_mac", gCore->deviceID());
    order.insert("waiter_code", getServerNumber());
    order.insert("table_number", getTableNumber());
    order.insert("time", QDateTime::currentDateTime().toString("yyyy-MM-dd hh:mm:ss"));

    QVariantList items;
    foreach (ITEMS::BILL_ITEM item,  sentItems) {
        QVariantMap menu_item;
        QVariantList modifiers;
        menu_item.insert("item_number", item.menuID);
        menu_item.insert("item_price", item.price);
        menu_item.insert("item_name", item.itemname);

        foreach (ITEMS::ModifierRepItem option, item.options) {
            QVariantMap modifier;
            modifier.insert("item_number", option.itemno);
            modifier.insert("item_price", option.price);
            modifier.insert("item_name",  option.itemname);
            modifiers.append(modifier);
        }

        menu_item.insert("modifiers", modifiers);
        items.append(menu_item);
    }

    order.insert("items", items);

    return postJson(urlSuffix, order);
}


WebStorageResponse * WebStorage::saveGameSession(GameSessionData *session)
{
    QString urlSuffix = QString("game/");
    QVariantMap fields;

    fields.insert("restaurant_code", getRestaurantCode());
    fields.insert("pos_check_number", getCheckNumber());
    fields.insert("table_number", getTableNumber());
    fields.insert("waiter_code", getServerNumber());
    fields.insert("device_mac", gCore->deviceID());
    fields.insert("game_name", session->gameName);
    fields.insert("player_name", session->player);
    fields.insert("score", session->score);
    fields.insert("charge", session->charge);
    fields.insert("start_time", session->startTime.toString("yyyy-MM-dd hh:mm:ss"));
    fields.insert("played_seconds", session->played_seconds);
    fields.insert("level", session->level);

    QVariantList features;
    foreach (QString feature, session->features.keys()) {
        QVariantMap featureListItem;
        featureListItem.insert(QString("name"), feature);
        featureListItem.insert(QString("charge"), session->features.value(feature));
        features.append(featureListItem);
    }

    fields.insert("features", features);

    return postJson(urlSuffix, fields);
}


WebStorageResponse * WebStorage::saveDeviceInfo()
{
    QString urlSuffix = QString("device/");
    QVariantMap fields;

    fields.insert("restaurant_code", getRestaurantCode());
    fields.insert("mac", gCore->deviceID());
    fields.insert("ip", gCore->IPaddresses().size() > 0 ? gCore->IPaddresses().at(0) : "");
    fields.insert("software_revision", gCore->version());
    fields.insert("table", getTableNumber());
    fields.insert("waiter", getServerNumber());

    return postJson(urlSuffix, fields);
}
