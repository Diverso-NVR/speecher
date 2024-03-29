import os
from loguru import logger

from sound_text_class import SoundToText, SplitAudio
from drive_downloader import Drive
from youtube_downloader import Youtube
from erudite_api import Erudite


def convert_offline(records: list) -> None:
    record_keywords = {}
    for record in records:
        record_key = record["room_name"] + "_" + record["start_time"][:5]
        if not record_keywords.get(record_key):
            video_name = download_from_drive(record)
            key_words = convert(video_name)
        else:
            key_words = record_keywords[record_key]

        Erudite.patch_record(key_words, record["id"])


def convert_zoom(records: list) -> None:
    for record in records:
        video_name = download_from_drive(record)
        key_words = convert(video_name)
        Erudite.patch_record(key_words, record["id"])


def convert_jitsi(records: list) -> None:
    for record in records:
        video_name = download_from_youtube(record)
        if video_name:
            key_words = convert(video_name)
            Erudite.patch_record(key_words, record["id"])


def download_from_youtube(record: dict) -> bool or str:
    vid, name = Youtube.download(record["url"])
    if vid:
        logger.info(f"Video - {vid} downloaded")
        video_name = name.split(".")[0]
        return video_name


def download_from_drive(record: dict) -> str:
    id = record["url"].split("/")[-2]
    drive = Drive()
    drive.download(id)
    video_name = drive.file_name.split(".")[0]
    return video_name


def convert(video_name: str) -> list:
    SoundToText.video_to_sound(video_name)

    split_wav = SplitAudio(SoundToText.SOUND_WAV)
    names_list = split_wav.multiple_split()
    words = SoundToText.convert_audio_to_text(names_list, "ru-RU")
    key_words = SoundToText.clear_words(words)
    os.remove(f"{video_name}.mp4")
    return list(key_words)


@logger.catch
def main():
    records = Erudite.get_all_records_per_day()
    offline, zoom, jitsi = Erudite.filter_records(records)

    # convert_offline(offline)
    convert_zoom(zoom)
    convert_jitsi(jitsi)


if __name__ == "__main__":
    main()
