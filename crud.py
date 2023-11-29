import asyncio

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, User, Profile, Post, Order, Product, OrderProductAssociation


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


async def main_relations(session: AsyncSession):
    await create_user(session=session, username='join')
    await create_user(session=session, username='sam')
    await create_user(session=session, username='alice')

    user_sam = await get_user_by_username(session=session, username="sam")
    user_john = await get_user_by_username(session=session, username="join")
    await get_user_by_username(session=session, username="sam")
    await get_user_by_username(session=session, username="bob")

    if user_sam and user_john:
        await create_user_profile(
            session=session,
            user_id=user_sam.id,
            first_name="Сэм",
            last_name="Егоров"
        )
        await create_user_profile(
            session=session,
            user_id=user_john.id,
            first_name="Джон"
        )

    users = await show_users_with_profiles(session)
    print(users)

    if user_sam and user_john:
        john_posts = await create_posts(
            session,
            user_john.id,
            'SQL SELECT',
            'SQL JOIN',
        )
        sam_posts = await create_posts(
            session,
            user_sam.id,
            'SQL WHERE',
            'SQL FROM',
        )
        print(john_posts)
        print(sam_posts)

    await get_users_with_posts(session)
    await get_post_with_user(session)
    await get_users_with_posts_and_profiles(session)
    await get_profile_with_users_and_users_with_posts(session)


async def create_order(session: AsyncSession, promocode: str | None = None) -> Order:
    order = Order(promocode=promocode)

    session.add(order)
    await session.commit()

    return order


async def create_product(
        session: AsyncSession,
        name: str,
        description: str,
        price: int,
) -> Product:
    product = Product(
        name=name,
        description=description,
        price=price,
    )

    session.add(product)
    await session.commit()
    return product


async def create_orders_and_products(session: AsyncSession):
    order_one = await create_order(session)
    order_promo = await create_order(session, promocode='promo')

    mouse = await create_product(
        session,
        'Mouse',
        'Great gaming mouse',
        120,
    )
    keyboard = await create_product(
        session,
        'Keyboard',
        'Great gaming keyboard',
        149,
    )
    display = await create_product(
        session,
        'Display',
        'Office display',
        249,
    )

    order_one = await session.scalar(
        select(Order)
        .where(Order.id == order_one.id)
        .options(
            selectinload(Order.products),
        ),
    )
    order_promo = await session.scalar(
        select(Order)
        .where(Order.id == order_promo.id)
        .options(
            selectinload(Order.products),
        ),
    )

    order_one.products.append(mouse)
    order_one.products.append(keyboard)
    # order_promo.products.append(keyboard)
    # order_promo.products.append(display)
    order_promo.products = [keyboard, display]

    await session.commit()


async def get_orders_with_products_secondary(sesstion: AsyncSession) -> list[Order]:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.products),
        )
        .order_by(Order.id)
    )
    orders = await sesstion.scalars(stmt)
    return list(orders)


async def demo_get_orders_with_products_through_secondary(session: AsyncSession):

    orders = await get_orders_with_products_secondary(session)
    for order in orders:
        print(order.id, order.promocode, order.created_at, 'products:')
        for product in order.products:
            print('-', product.id, product.name, product.price)


async def get_orders_with_products_with_association(sesstion: AsyncSession) -> list[Order]:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.products_details).joinedload(
                OrderProductAssociation.product
            ),
        )
        .order_by(Order.id)
    )
    orders = await sesstion.scalars(stmt)
    return list(orders)


async def demo_get_orders_with_products_with_association(session: AsyncSession):
    orders = await get_orders_with_products_with_association(session)

    for order in orders:
        print(order.id, order.promocode, order.created_at, 'products:')
        for order_product_detail in order.products_details:
            print('-', order_product_detail.product.id, order_product_detail.product.name,
                  order_product_detail.product.price, 'quantity:', order_product_detail.count)


async def create_gift_product_for_existing_orders(session: AsyncSession):
    orders = await get_orders_with_products_with_association(session)
    gift_product = await create_product(
        session,
        name='Gift',
        description='Gift for you',
        price=0,
    )
    for order in orders:
        order.products_details.append(
            OrderProductAssociation(
                count=1,
                unit_price=0,
                product=gift_product,
            )
        )

    await session.commit()


async def demo_m2m(session: AsyncSession):
    # await create_orders_and_products(session)
    # await demo_get_orders_with_products_through_secondary(session)
    await demo_get_orders_with_products_with_association(session)
    # await create_gift_product_for_existing_orders(session)


async def main():
    async with db_helper.session_factory() as session:
        # await main_relations(session)
        await demo_m2m(session)


if __name__ == "__main__":
    asyncio.run(main())
