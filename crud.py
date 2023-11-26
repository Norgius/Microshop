import asyncio

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, User, Profile, Post


async def create_user(session: AsyncSession, username: str) -> User:
    user = User(username=username)
    session.add(user)
    await session.commit()
    print("User", user)
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    # Либо в 2 строки, либо в одну, как указано ниже
    # result: Result = await session.execute(stmt)
    # user: User | None = result.scalar_one_or_none()
    user: User | None = await session.scalar(stmt)
    print("Found user", username, user)
    return user


async def show_users_with_profiles(session: AsyncSession) -> list[User]:
    stmt = select(User).options(joinedload(User.profile)).order_by(User.id)
    # result: Result = await session.execute(stmt)
    # users = result.scalars()
    users = await session.scalars(stmt)
    # for user in users:
    #     print(user.profile.first_name)
    return list(users)


async def create_posts(
        session: AsyncSession,
        user_id: int,
        *posts_titles: str
):
    posts = [
        Post(user_id=user_id, title=title)
        for title in posts_titles
    ]
    session.add_all(posts)
    await session.commit()
    return posts


async def get_users_with_posts(session: AsyncSession):
    stmt = select(User).options(
        # joinedload(User.posts)
        selectinload(User.posts)
    ).order_by(User.username)
    users = await session.scalars(stmt)

    # result: Result = await session.execute(stmt)
    # users = result.scalars()

    # for user in users.unique():
    for user in users:
        print(f"User: {user} has posts:")
        if user.posts:
            for post in user.posts:
                print("*", post.title)
        else:
            print(f"У user {user.username} нет постов")


async def get_users_with_posts_and_profiles(session: AsyncSession):
    stmt = select(User).options(
        joinedload(User.profile),
        selectinload(User.posts)
    ).order_by(User.username)
    users = await session.scalars(stmt)

    # result: Result = await session.execute(stmt)
    # users = result.scalars()

    # for user in users.unique():
    for user in users:
        print("Профиль user - ", user.profile and user.profile.first_name)
        print(f"User: {user.username} has posts:")
        if user.posts:
            for post in user.posts:
                print("*", post.title)
        else:
            print(f"У user {user.username} нет постов")


async def get_profile_with_users_and_users_with_posts(session: AsyncSession):
    stmt = (
        select(Profile)
        .join(Profile.user)
        .options(
            joinedload(Profile.user).selectinload(User.posts),
        )
        .where(User.username == "sam")
        .order_by(Profile.id)
    )
    profiles = await session.scalars(stmt)

    for profile in profiles:
        print(profile.first_name, profile.last_name, profile.user)
        print('Посты этого пользователя:')
        for post in profile.user.posts:
            print(post)


async def get_post_with_user(session: AsyncSession):
    stmt = select(Post).options(joinedload(Post.user)).order_by(Post.id)

    posts = await session.scalars(stmt)

    for post in posts:
        print(f"Пост {post.title} пользователя {post.user.username}")


async def create_user_profile(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
) -> Profile:
    profile = Profile(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
    )
    session.add(profile)
    await session.commit()
    return profile


async def main():
    async with db_helper.session_factory() as session:
        # await create_user(session=session, username='join')
        # await create_user(session=session, username='sam')
        # await create_user(session=session, username='alice')

        # user_sam = await get_user_by_username(session=session, username="sam")
        # user_john = await get_user_by_username(session=session, username="join")
        # await get_user_by_username(session=session, username="sam")
        # await get_user_by_username(session=session, username="bob")

        # await create_user_profile(
        #     session=session,
        #     user_id=user_sam.id,
        #     first_name="Сэм",
        #     last_name="Егоров"
        # )
        # await create_user_profile(
        #     session=session,
        #     user_id=user_john.id,
        #     first_name="Джон"
        # )

        # users = await show_users_with_profiles(session)
        # print(users)

        # john_posts = await create_posts(
        #     session,
        #     user_john.id,
        #     'SQL SELECT',
        #     'SQL JOIN',
        # )
        # sam_posts = await create_posts(
        #     session,
        #     user_sam.id,
        #     'SQL WHERE',
        #     'SQL FROM',
        # )
        # print(john_posts)
        # print(sam_posts)

        # await get_users_with_posts(session)
        # await get_post_with_user(session)
        # await get_users_with_posts_and_profiles(session)
        await get_profile_with_users_and_users_with_posts(session)


if __name__ == "__main__":
    asyncio.run(main())
